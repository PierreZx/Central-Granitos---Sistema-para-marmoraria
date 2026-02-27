using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;
using System.Linq;

namespace Marmorariacentral.ViewModels
{
    [QueryProperty(nameof(ClienteSelecionado), "Cliente")]
    public partial class DetalhesClienteViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;

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
                    catch (Exception ex) { System.Diagnostics.Debug.WriteLine($"Erro Firebase Peca: {ex.Message}"); }
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
            catch (Exception ex) { System.Diagnostics.Debug.WriteLine($"Erro ao carregar peças: {ex.Message}"); }
        }

        private void AtualizarTotal() 
        {
            ValorTotalGeral = ListaPecas.Sum(p => p.ValorTotalPeca);
            OnPropertyChanged(nameof(ValorTotalGeral));
        }

        [RelayCommand]
        private async Task IrParaCalculadora()
        {
            await Shell.Current.GoToAsync("CalculadoraPecaPage", new Dictionary<string, object>
            {
                { "ClienteSelecionado", ClienteSelecionado }
            });
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
            bool confirmar = await Shell.Current.DisplayAlert("Excluir", $"Deseja remover a peça '{peca.Ambiente}'?", "Sim", "Não");
            if (confirmar)
            {
                await _dbService.DeleteItemAsync(peca);
                ListaPecas.Remove(peca);
                AtualizarTotal();
            }
        }

        // ==========================================
        // LÓGICA DE LANÇAMENTO FINANCEIRO (CORRIGIDA)
        // ==========================================
        [RelayCommand]
        private async Task LancarNoFinanceiro()
        {
            if (ListaPecas.Count == 0)
            {
                await Shell.Current.DisplayAlert("Aviso", "Adicione peças ao orçamento antes de lançar!", "OK");
                return;
            }

            bool confirmar = await Shell.Current.DisplayAlert("Confirmar", 
                $"Deseja lançar {ValorTotalGeral:C} no financeiro?", "Sim", "Não");

            if (!confirmar) return;

            var novoLancamento = new FinanceiroRegistro
            {
                Id = Guid.NewGuid().ToString(),
                Descricao = $"Orçamento: {ClienteSelecionado.Nome}",
                Valor = ValorTotalGeral,
                Tipo = "Entrada",
                DataVencimento = DateTime.Now,
                FoiPago = false,
                IsParcelado = false
            };

            try
            {
                await _dbService.SaveItemAsync(novoLancamento);
                await _firebaseService.SaveFinanceiroAsync(novoLancamento);

                await Shell.Current.DisplayAlert("Sucesso", "Orçamento enviado para a aba 'ORÇAMENTOS' no Financeiro.", "OK");
                
                // CORREÇÃO: Voltamos uma tela em vez de tentar pular para a aba absoluta
                await Shell.Current.GoToAsync(".."); 
            }
            catch (Exception ex)
            {
                await Shell.Current.DisplayAlert("Erro", "Erro ao salvar: " + ex.Message, "OK");
            }
        }
    }
}