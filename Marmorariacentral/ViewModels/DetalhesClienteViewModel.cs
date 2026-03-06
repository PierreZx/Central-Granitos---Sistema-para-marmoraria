using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Linq;

namespace Marmorariacentral.ViewModels
{
    [QueryProperty(nameof(ClienteSelecionado), "Cliente")]
    public partial class DetalhesClienteViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;
        private readonly PdfService _pdfService = new();

        [ObservableProperty] private Cliente clienteSelecionado = new();
        [ObservableProperty] private ObservableCollection<PecaOrcamento> listaPecas = new();
        [ObservableProperty] private double valorTotalGeral;

        public DetalhesClienteViewModel(DatabaseService dbService, FirebaseService firebaseService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
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
            catch { }
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
            if (await Shell.Current.DisplayAlert("Excluir", $"Remover '{peca.Ambiente}'?", "Sim", "Não"))
            {
                await _dbService.DeleteItemAsync(peca);
                ListaPecas.Remove(peca);
                AtualizarTotal();
            }
        }

        [RelayCommand]
        public async Task GerarPdfTecnico(View viewParaCapturar) // Alterado de GraphicsView para View
        {
            if (ListaPecas.Count == 0)
            {
                await Shell.Current.DisplayAlert("Aviso", "Não há peças no orçamento.", "OK");
                return;
            }

            if (ClienteSelecionado == null || viewParaCapturar == null)
                return;

            try
            {
                await _pdfService.GerarPdfTecnicoAsync(
                    ClienteSelecionado,
                    ListaPecas.ToList(),
                    viewParaCapturar
                );
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro ao gerar PDF Técnico: {ex.Message}");
            }
        }

        [RelayCommand]
        public async Task GerarOrcamentoPdf(View viewParaCapturar) // Alterado de GraphicsView para View
        {
            if (ListaPecas.Count == 0)
            {
                await Shell.Current.DisplayAlert("Aviso", "Não há peças no orçamento.", "OK");
                return;
            }

            if (ClienteSelecionado == null || viewParaCapturar == null)
                return;

            try
            {
                await _pdfService.GerarPdfClienteAsync(
                    ClienteSelecionado,
                    ListaPecas.ToList(),
                    viewParaCapturar
                );
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro ao gerar PDF Cliente: {ex.Message}");
            }
        }

        [RelayCommand]
        private async Task LancarNoFinanceiro()
        {
            if (ListaPecas.Count == 0) return;
            if (!await Shell.Current.DisplayAlert("Confirmar", $"Lançar {ValorTotalGeral:C}?", "Sim", "Não")) return;

            var lancamento = new FinanceiroRegistro {
                Descricao = $"Orçamento: {ClienteSelecionado.Nome}",
                Valor = ValorTotalGeral,
                Tipo = "Entrada",
                DataVencimento = DateTime.Now,
                FoiPago = false
            };

            await _dbService.SaveItemAsync(lancamento);
            await _firebaseService.SaveFinanceiroAsync(lancamento);
            await Shell.Current.DisplayAlert("Sucesso", "Enviado ao Financeiro!", "OK");
            await Shell.Current.GoToAsync(".."); 
        }
    }
}