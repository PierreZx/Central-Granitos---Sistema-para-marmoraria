using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;

namespace Marmorariacentral.ViewModels
{
    [QueryProperty(nameof(Cliente), "Cliente")]
    public partial class DetalhesClienteViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;

        [ObservableProperty]
        private Cliente cliente = new();

        [ObservableProperty]
        private ObservableCollection<PecaOrcamento> pecasAdicionadas = new();

        [ObservableProperty]
        private double totalOrcamento;

        public DetalhesClienteViewModel(DatabaseService dbService)
        {
            _dbService = dbService;
        }

        public async void ApplyQueryAttributes(IDictionary<string, object> query)
        {
            if (query.TryGetValue("Cliente", out var clientObj) && clientObj is Cliente c)
            {
                Cliente = c;
                await CarregarPecasDoBanco(); // Carrega o que já existe salvo
            }

            if (query.TryGetValue("NovaPeca", out var pecaObj) && pecaObj is PecaOrcamento novaPeca)
            {
                novaPeca.ClienteId = Cliente.Id; // Vincula ao cliente atual
                await _dbService.SaveItemAsync(novaPeca); // SALVA NO SQLITE
                await CarregarPecasDoBanco();
                query.Remove("NovaPeca");
            }
        }

        private async Task CarregarPecasDoBanco()
        {
            var todas = await _dbService.GetItemsAsync<PecaOrcamento>();
            var filtradas = todas.Where(p => p.ClienteId == Cliente.Id).ToList();
            
            MainThread.BeginInvokeOnMainThread(() => {
                PecasAdicionadas.Clear();
                foreach (var p in filtradas) PecasAdicionadas.Add(p);
                AtualizarTotal();
            });
        }

        private void AtualizarTotal() => TotalOrcamento = PecasAdicionadas.Sum(p => p.ValorTotalPeca);

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
            bool confirmar = await Shell.Current.DisplayAlert("Confirmar", $"Excluir a peça '{peca.Ambiente}'?", "Sim", "Não");
            if (confirmar)
            {
                await _dbService.DeleteItemAsync(peca); // REMOVE DO BANCO
                await CarregarPecasDoBanco();
            }
        }
    }
}