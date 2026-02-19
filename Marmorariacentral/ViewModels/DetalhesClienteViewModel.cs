using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;
using System.Linq;
using System.Diagnostics;

namespace Marmorariacentral.ViewModels
{
    [QueryProperty(nameof(ClienteSelecionado), "Cliente")]
    public partial class DetalhesClienteViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;
        private readonly PdfService _pdfService;

        private Cliente _clienteSelecionado = new();
        public Cliente ClienteSelecionado 
        { 
            get => _clienteSelecionado; 
            set => SetProperty(ref _clienteSelecionado, value); 
        }

        private ObservableCollection<PecaOrcamento> _listaPecas = new();
        public ObservableCollection<PecaOrcamento> ListaPecas 
        { 
            get => _listaPecas; 
            set => SetProperty(ref _listaPecas, value); 
        }

        private double _valorTotalGeral;
        public double ValorTotalGeral 
        { 
            get => _valorTotalGeral; 
            set => SetProperty(ref _valorTotalGeral, value); 
        }

        public DetalhesClienteViewModel(
            DatabaseService dbService, 
            FirebaseService firebaseService,
            PdfService pdfService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            _pdfService = pdfService;
        }

        [RelayCommand]
            private async Task GerarPdf()
            {
                if (!ListaPecas.Any())
                {
                    await Shell.Current.DisplayAlert("Aviso", "Adicione pelo menos uma peça antes de gerar o PDF.", "OK");
                    return;
                }

                try
                {
                    var orcamento = new Orcamento
                    {
                        Id = ClienteSelecionado.Id, // Use o ID do cliente como referência
                        NomeCliente = ClienteSelecionado.Nome,
                        Contato = ClienteSelecionado.Contato,
                        Endereco = ClienteSelecionado.Endereco,
                        ValorTotal = ValorTotalGeral,
                        DataCriacao = DateTime.Now
                    };

                    var caminho = await _pdfService.GerarOrcamentoPdfAsync(orcamento, ListaPecas.ToList());

                    await Launcher.OpenAsync(new OpenFileRequest
                    {
                        File = new ReadOnlyFile(caminho)
                    });
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"Erro ao gerar PDF: {ex.Message}");
                    await Shell.Current.DisplayAlert("Erro", "Falha ao gerar PDF.", "OK");
                }
            }

        public async void ApplyQueryAttributes(IDictionary<string, object> query)
        {
            if (query.TryGetValue("Cliente", out var clientObj) && clientObj is Cliente c)
            {
                ClienteSelecionado = c;
                await CarregarDadosCompletos();
            }

            if (query.TryGetValue("NovaPeca", out var pecaObj) && pecaObj is PecaOrcamento pecaRetornada)
            {
                pecaRetornada.ClienteId = ClienteSelecionado.Id;
                await _dbService.SaveItemAsync(pecaRetornada);
                
                _ = Task.Run(async () => {
                    try { await _firebaseService.SavePecaOrcamentoAsync(pecaRetornada); }
                    catch (Exception ex) { Debug.WriteLine($"Erro Firebase Peca: {ex.Message}"); }
                });

                await CarregarPecasDoBanco();
                query.Remove("NovaPeca");
            }
        }

        private async Task CarregarDadosCompletos()
        {
            await CarregarPecasDoBanco();
            try 
            {
                var pecasNuvem = await _firebaseService.GetPecasPorClienteAsync(ClienteSelecionado.Id);
                if (pecasNuvem != null && pecasNuvem.Any())
                {
                    foreach (var p in pecasNuvem) await _dbService.SaveItemAsync(p);
                    await CarregarPecasDoBanco();
                }
            }
            catch (Exception ex) { Debug.WriteLine($"Sincronização Cloud: {ex.Message}"); }
        }

        private async Task CarregarPecasDoBanco()
        {
            try 
            {
                var todas = await _dbService.GetItemsAsync<PecaOrcamento>();
                var filtradas = todas.Where(p => p.ClienteId == ClienteSelecionado.Id).ToList();
                
                MainThread.BeginInvokeOnMainThread(() => {
                    ListaPecas.Clear();
                    foreach (var p in filtradas) ListaPecas.Add(p);
                    AtualizarTotal();
                });
            }
            catch (Exception ex) { Debug.WriteLine($"Erro ao carregar peças: {ex.Message}"); }
        }

        private void AtualizarTotal() 
        {
            ValorTotalGeral = ListaPecas.Sum(p => p.ValorTotalPeca);
            OnPropertyChanged(nameof(ValorTotalGeral));
        }

        [RelayCommand]
        private async Task IrParaCalculadora()
        {
            await Shell.Current.GoToAsync("CalculadoraPecaPage", new Dictionary<string, object> { { "ClienteSelecionado", ClienteSelecionado } });
        }

        [RelayCommand]
        private async Task EditarPeca(PecaOrcamento peca)
        {
            if (peca == null) return;
            await Shell.Current.GoToAsync("CalculadoraPecaPage", new Dictionary<string, object> { ["PecaParaEditar"] = peca });
        }

        [RelayCommand]
        private async Task RemoverPeca(PecaOrcamento peca)
        {
            if (peca == null) return;

            bool confirmar = await Shell.Current.DisplayAlert("Excluir Peça", $"Deseja remover a peça do ambiente '{peca.Ambiente}'?", "Sim", "Não");
            if (!confirmar) return;

            try
            {
                await _dbService.DeleteItemAsync(peca);
                await _firebaseService.DeletePecaOrcamentoAsync(peca.Id); // Corrigido aqui
                ListaPecas.Remove(peca);
                AtualizarTotal();
            }
            catch (Exception ex) { Debug.WriteLine($"Erro ao remover: {ex.Message}"); }
        }

        [RelayCommand]
        private async Task SalvarOrcamentoFinal()
        {
            await Shell.Current.DisplayAlert("Sucesso", "Orçamento atualizado!", "OK");
        }
    }
}