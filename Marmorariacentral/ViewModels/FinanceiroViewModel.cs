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

        private List<FinanceiroRegistro> _todasAsContas = new();

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

        private double _saldoTotal;
        public double SaldoTotal
        {
            get => _saldoTotal;
            set => SetProperty(ref _saldoTotal, value);
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
                _todasAsContas = lista.ToList();

                MainThread.BeginInvokeOnMainThread(() =>
                {
                    AtualizarListasVisuais(_todasAsContas);
                    CalcularSaldo();
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro ao carregar financeiro: {ex.Message}");
            }
        }

        private void AtualizarListasVisuais(List<FinanceiroRegistro> lista)
        {
            ContasAtivas.Clear();
            ExtratoDia.Clear();

            foreach (var item in lista.OrderBy(x => x.DataVencimento))
            {
                item.StatusColor = CalcularCorStatus(item.DataVencimento);

                if (!item.FoiPago)
                    ContasAtivas.Add(item);
                else
                    ExtratoDia.Add(item);
            }
        }

        private void CalcularSaldo()
        {
            var entradas = _todasAsContas
                .Where(x => x.FoiPago && x.Tipo == "Entrada")
                .Sum(x => x.Valor);

            var saidas = _todasAsContas
                .Where(x => x.FoiPago && x.Tipo == "Saida")
                .Sum(x => x.Valor);

            SaldoTotal = entradas - saidas;
        }

        [RelayCommand]
        public void Filtrar(string texto)
        {
            if (string.IsNullOrWhiteSpace(texto))
            {
                AtualizarListasVisuais(_todasAsContas);
                return;
            }

            var filtrados = _todasAsContas
                .Where(x =>
                    x.Descricao.ToLower().Contains(texto.ToLower()) ||
                    x.Valor.ToString().Contains(texto))
                .ToList();

            AtualizarListasVisuais(filtrados);
        }

        public void OrdenarLista(string criterio)
        {
            IEnumerable<FinanceiroRegistro> ordenado = _todasAsContas;

            switch (criterio)
            {
                case "Vencimento":
                    ordenado = _todasAsContas.OrderBy(x => x.DataVencimento);
                    break;

                case "Maior Valor":
                    ordenado = _todasAsContas.OrderByDescending(x => x.Valor);
                    break;

                case "Menor Valor":
                    ordenado = _todasAsContas.OrderBy(x => x.Valor);
                    break;
            }

            AtualizarListasVisuais(ordenado.ToList());
        }

        private Color CalcularCorStatus(DateTime vencimento)
        {
            var hoje = DateTime.Today;

            if (vencimento.Date <= hoje)
                return Color.FromArgb("#FF0000");

            if ((vencimento - hoje).TotalDays <= 4)
                return Color.FromArgb("#FFD700");

            return Color.FromArgb("#008000");
        }

        [RelayCommand]
        public async Task ConfirmarPagamento(FinanceiroRegistro registro)
        {
            if (registro == null) return;

            bool confirmar = await Shell.Current.DisplayAlert(
                "Confirmar pagamento",
                $"Marcar '{registro.Descricao}' como pago?",
                "Sim",
                "Cancelar");

            if (!confirmar)
            {
                registro.FoiPago = false;
                return;
            }

            registro.FoiPago = true;

            await _dbService.SaveItemAsync(registro);

            try
            {
                await _firebaseService.SaveFinanceiroAsync(registro);
            }
            catch { }

            await CarregarDados();
        }

        [RelayCommand]
        public async Task AbrirCadastro()
        {
            var popup = new CadastroFinanceiroPopup();
            var resultado = await Shell.Current.ShowPopupAsync(popup);

            if (resultado is FinanceiroRegistro novo)
            {
                await SalvarRegistroFull(novo);
                await CarregarDados();
            }
        }

        [RelayCommand]
        public async Task AbrirLancamentoExtrato()
        {
            // O parâmetro 'true' ativa o modo simplificado no popup
            var popup = new CadastroFinanceiroPopup(null, true); 
            var resultado = await Shell.Current.ShowPopupAsync(popup);

            if (resultado is FinanceiroRegistro novo)
            {
                await SalvarRegistroFull(novo);
                await CarregarDados();
            }
        }

        [RelayCommand]
        public async Task EditarRegistro(FinanceiroRegistro registro)
        {
            if (registro == null) return;

            var popup = new CadastroFinanceiroPopup(registro);
            var resultado = await Shell.Current.ShowPopupAsync(popup);

            if (resultado is FinanceiroRegistro editado)
            {
                await SalvarRegistroFull(editado);
                await CarregarDados();
            }
        }

        [RelayCommand]
        public async Task ExcluirRegistro(FinanceiroRegistro registro)
        {
            if (registro == null) return;

            bool confirmar = await Shell.Current.DisplayAlert(
                "Excluir",
                $"Excluir '{registro.Descricao}'?",
                "Sim",
                "Cancelar");

            if (!confirmar) return;

            await _dbService.DeleteItemAsync(registro);
            await CarregarDados();
        }

        private async Task SalvarRegistroFull(FinanceiroRegistro reg)
        {
            await _dbService.SaveItemAsync(reg);

            try
            {
                await _firebaseService.SaveFinanceiroAsync(reg);
            }
            catch { }
        }
    }
}