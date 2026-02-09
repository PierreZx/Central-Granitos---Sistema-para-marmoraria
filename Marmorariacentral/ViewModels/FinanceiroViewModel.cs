using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;

namespace Marmorariacentral.ViewModels
{
    public partial class FinanceiroViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;

        [ObservableProperty]
        private ObservableCollection<FinanceiroRegistro> contasFixas = new();

        public FinanceiroViewModel(DatabaseService dbService, FirebaseService firebaseService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            Task.Run(async () => await CarregarFinanceiro());
        }

        [RelayCommand]
        public async Task CarregarFinanceiro()
        {
            var lista = await _dbService.GetItemsAsync<FinanceiroRegistro>();
            MainThread.BeginInvokeOnMainThread(() =>
            {
                ContasFixas.Clear();
                foreach (var item in lista)
                    ContasFixas.Add(item);
            });
        }

        // Lógica para definir a cor da bolinha no esqueleto
        public Color GetStatusColor(DateTime vencimento)
        {
            var diasParaVencer = (vencimento - DateTime.Now).TotalDays;

            if (diasParaVencer < 0) return Colors.Red; // Vencido
            if (diasParaVencer <= 4) return Colors.Yellow; // Próximo
            return Colors.Green; // No prazo
        }
    }
}