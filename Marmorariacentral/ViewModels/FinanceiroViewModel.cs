using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using Marmorariacentral.Views.Financeiro;
using System.Collections.ObjectModel;
using System.Diagnostics;

#pragma warning disable CA1416 // Silencia avisos de plataforma do Windows

namespace Marmorariacentral.ViewModels
{
    public partial class FinanceiroViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;

        // Propriedades Manuais para evitar erros de gerador de código
        private ObservableCollection<FinanceiroRegistro> _contasAtivas = new();
        public ObservableCollection<FinanceiroRegistro> ContasAtivas 
        { 
            get => _contasAtivas; 
            set => SetProperty(ref _contasAtivas, value); 
        }

        private ObservableCollection<FinanceiroRegistro> _extratoDia = new();
        public ObservableCollection<FinanceiroRegistro> ExtratoDia 
        { 
            get => _extratoDia; 
            set => SetProperty(ref _extratoDia, value); 
        }

        public FinanceiroViewModel(DatabaseService dbService, FirebaseService firebaseService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            _ = CarregarDados();
        }

        [RelayCommand]
        public async Task CarregarDados()
        {
            try
            {
                var lista = await _dbService.GetItemsAsync<FinanceiroRegistro>();
                
                MainThread.BeginInvokeOnMainThread(() =>
                {
                    ContasAtivas.Clear();
                    ExtratoDia.Clear();

                    foreach (var item in lista)
                    {
                        // Calcula a cor baseada no vencimento
                        item.StatusColor = CalcularCorStatus(item.DataVencimento);

                        if (!item.FoiPago)
                            ContasAtivas.Add(item);
                        else
                            ExtratoDia.Add(item);
                    }
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro ao carregar financeiro: {ex.Message}");
            }
        }

        private Color CalcularCorStatus(DateTime vencimento)
        {
            var hoje = DateTime.Today;
            var diasParaVencer = (vencimento - hoje).TotalDays;

            if (diasParaVencer < 0) return Color.FromArgb("#FF0000"); // Vermelho (Vencido)
            if (diasParaVencer <= 4) return Color.FromArgb("#FFD700"); // Amarelo (Próximo)
            return Color.FromArgb("#008000"); // Verde (No prazo)
        }

        [RelayCommand]
        public async Task ConfirmarPagamento(FinanceiroRegistro registro)
        {
            if (registro == null) return;

            registro.FoiPago = true;

            // Lógica de Recorrência Mensal
            if (registro.IsFixo)
            {
                var proximoMes = new FinanceiroRegistro
                {
                    Descricao = registro.Descricao,
                    Valor = registro.Valor,
                    DataVencimento = registro.DataVencimento.AddMonths(1),
                    IsFixo = true,
                    Tipo = registro.Tipo
                };
                await _dbService.SaveItemAsync(proximoMes);
            }
            // Lógica de Parcelamento
            else if (registro.IsParcelado && registro.ParcelaAtual < registro.TotalParcelas)
            {
                var proximaParcela = new FinanceiroRegistro
                {
                    Descricao = registro.Descricao,
                    Valor = registro.Valor,
                    DataVencimento = registro.DataVencimento.AddMonths(1),
                    IsParcelado = true,
                    ParcelaAtual = registro.ParcelaAtual + 1,
                    TotalParcelas = registro.TotalParcelas,
                    Tipo = registro.Tipo
                };
                await _dbService.SaveItemAsync(proximaParcela);
            }

            await _dbService.SaveItemAsync(registro);
            await CarregarDados();
        }

        [RelayCommand]
        public async Task AbrirCadastro()
        {
            var popup = new CadastroFinanceiroPopup();
            var resultado = await Shell.Current.ShowPopupAsync(popup);

            if (resultado is FinanceiroRegistro novo)
            {
                await _dbService.SaveItemAsync(novo);
                await CarregarDados();
            }
        }

        [RelayCommand]
        public async Task EditarRegistro(FinanceiroRegistro registro)
        {
            if (registro == null) return;

            // Reutiliza o popup passando o registro para edição
            var popup = new CadastroFinanceiroPopup(registro);
            var resultado = await Shell.Current.ShowPopupAsync(popup);

            if (resultado is FinanceiroRegistro editado)
            {
                await _dbService.SaveItemAsync(editado);
                await CarregarDados();
            }
        }

        [RelayCommand]
        public async Task ExcluirRegistro(FinanceiroRegistro registro)
        {
            if (registro == null) return;

            bool confirmar = await Shell.Current.DisplayAlert(
                "Atenção", 
                $"Deseja excluir '{registro.Descricao}' permanentemente?", 
                "Sim", 
                "Não");

            if (confirmar)
            {
                await _dbService.DeleteItemAsync(registro);
                await CarregarDados();
            }
        }
    }
}