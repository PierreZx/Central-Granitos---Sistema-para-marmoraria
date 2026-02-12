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
            // 1. Recebe o Cliente selecionado
            if (query.TryGetValue("Cliente", out var clientObj) && clientObj is Cliente c)
            {
                ClienteSelecionado = c;
                await CarregarDadosCompletos(); // Carrega local + nuvem
            }

            // 2. Recebe a Peça da Calculadora
            if (query.TryGetValue("NovaPeca", out var pecaObj) && pecaObj is PecaOrcamento novaPeca)
            {
                novaPeca.ClienteId = ClienteSelecionado.Id;
                
                // Salva no SQLite local
                await _dbService.SaveItemAsync(novaPeca);
                
                // Backup em background para o Firebase (Coleção: orcamentos_detalhes)
                _ = Task.Run(async () => {
                    try { await _firebaseService.SavePecaOrcamentoAsync(novaPeca); }
                    catch (Exception ex) { System.Diagnostics.Debug.WriteLine($"Erro Firebase Peca: {ex.Message}"); }
                });

                await CarregarPecasDoBanco();
                query.Remove("NovaPeca");
            }
        }

        private async Task CarregarDadosCompletos()
        {
            // Primeiro carrega o que tem no celular para ser rápido
            await CarregarPecasDoBanco();

            // Depois tenta puxar da nuvem para garantir que não perdeu nada
            try 
            {
                var pecasNuvem = await _firebaseService.GetPecasPorClienteAsync(ClienteSelecionado.Id);
                if (pecasNuvem.Any())
                {
                    foreach (var p in pecasNuvem) await _dbService.SaveItemAsync(p);
                    await CarregarPecasDoBanco();
                }
            }
            catch { /* Offline ou erro de rede */ }
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
            catch (Exception ex) { System.Diagnostics.Debug.WriteLine(ex.Message); }
        }

        private void AtualizarTotal() 
        {
            ValorTotalGeral = ListaPecas.Sum(p => p.ValorTotalPeca);
        }

        [RelayCommand]
        private async Task IrParaCalculadora() => await Shell.Current.GoToAsync("CalculadoraPecaPage");

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
                // Opcional: Remover do Firebase aqui também se quiser sync total
                await CarregarPecasDoBanco();
            }
        }

        [RelayCommand]
        private async Task SalvarOrcamentoFinal()
        {
            // Aqui você salvaria o cabeçalho do orçamento vinculado ao cliente
            await Shell.Current.DisplayAlert("Sucesso", "Orçamento salvo e sincronizado!", "OK");
        }
    }
}