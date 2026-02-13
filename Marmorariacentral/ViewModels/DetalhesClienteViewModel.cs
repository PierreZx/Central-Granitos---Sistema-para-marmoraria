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
            // 1. Recebe o Cliente selecionado (Vindo da OrcamentosPage)
            if (query.TryGetValue("Cliente", out var clientObj) && clientObj is Cliente c)
            {
                ClienteSelecionado = c;
                await CarregarDadosCompletos(); // Carrega local + nuvem
            }

            // 2. Recebe a Peça retornada da CalculadoraPecaPage
            if (query.TryGetValue("NovaPeca", out var pecaObj) && pecaObj is PecaOrcamento pecaRetornada)
            {
                pecaRetornada.ClienteId = ClienteSelecionado.Id;
                
                // Salva no SQLite local
                await _dbService.SaveItemAsync(pecaRetornada);
                
                // Backup em background para o Firebase
                _ = Task.Run(async () => {
                    try { await _firebaseService.SavePecaOrcamentoAsync(pecaRetornada); }
                    catch (Exception ex) { System.Diagnostics.Debug.WriteLine($"Erro Firebase Peca: {ex.Message}"); }
                });

                await CarregarPecasDoBanco();
                
                // Limpa a query para evitar reprocessamento ao girar a tela
                query.Remove("NovaPeca");
            }
        }

        private async Task CarregarDadosCompletos()
        {
            // Carregamento imediato do banco local
            await CarregarPecasDoBanco();

            // Sincronização com a Nuvem (Firebase)
            try 
            {
                var pecasNuvem = await _firebaseService.GetPecasPorClienteAsync(ClienteSelecionado.Id);
                if (pecasNuvem != null && pecasNuvem.Any())
                {
                    foreach (var p in pecasNuvem) 
                    {
                        await _dbService.SaveItemAsync(p);
                    }
                    await CarregarPecasDoBanco();
                }
            }
            catch { /* Offline ou erro de rede silencioso */ }
        }

        private async Task CarregarPecasDoBanco()
        {
            try 
            {
                // Busca todas as peças do cliente atual no SQLite
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
            // Soma o valor de todas as peças para exibir no rodapé da página
            ValorTotalGeral = ListaPecas.Sum(p => p.ValorTotalPeca);
            OnPropertyChanged(nameof(ValorTotalGeral));
        }

        [RelayCommand]
        private async Task IrParaCalculadora()
        {
            var navigationParameter = new Dictionary<string, object>
            {
                { "ClienteSelecionado", ClienteSelecionado }
            };
            
            await Shell.Current.GoToAsync("CalculadoraPecaPage", navigationParameter);
        }

        [RelayCommand]
        private async Task EditarPeca(PecaOrcamento peca)
        {
            if (peca == null) return;
            
            await Shell.Current.GoToAsync("CalculadoraPecaPage", new Dictionary<string, object> 
            { 
                ["PecaParaEditar"] = peca 
            });
        }

        [RelayCommand]
        private async Task RemoverPeca(PecaOrcamento peca)
        {
            if (peca == null) return;
            
            bool confirmar = await Shell.Current.DisplayAlert("Excluir", 
                $"Deseja remover a peça '{peca.Ambiente}'?", "Sim", "Não");
            
            if (confirmar)
            {
                await _dbService.DeleteItemAsync(peca);
                ListaPecas.Remove(peca);
                AtualizarTotal();
            }
        }

        [RelayCommand]
        private async Task SalvarOrcamentoFinal()
        {
            await Shell.Current.DisplayAlert("Sucesso", "Orçamento atualizado com sucesso!", "OK");
        }
    }
}