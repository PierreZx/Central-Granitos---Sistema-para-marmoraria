using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using Marmorariacentral.Views.Financeiro;
using System.Collections.ObjectModel;
using System.Diagnostics;
using Shiny.Notifications;

#pragma warning disable CA1416 

namespace Marmorariacentral.ViewModels
{
    public partial class FinanceiroViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;
        private readonly INotificationManager? _notificationManager;

        private List<FinanceiroRegistro> _todasAsContas = new();

        [ObservableProperty]
        private ObservableCollection<FinanceiroRegistro> contasPendentes = new();

        [ObservableProperty]
        private ObservableCollection<FinanceiroRegistro> extratoGeral = new();

        [ObservableProperty]
        private double saldoTotal;

        public FinanceiroViewModel(DatabaseService dbService, FirebaseService firebaseService, INotificationManager? notificationManager = null)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            _notificationManager = notificationManager;
            _ = CarregarDados();
        }

        [RelayCommand]
        public async Task CarregarDados()
        {
            try
            {
                if (_notificationManager != null)
                {
                    try { await _notificationManager.RequestAccess(); } catch { }
                }

                var lista = await _dbService.GetItemsAsync<FinanceiroRegistro>();
                _todasAsContas = lista?.ToList() ?? new List<FinanceiroRegistro>();

                MainThread.BeginInvokeOnMainThread(() =>
                {
                    DistribuirListas(_todasAsContas);
                    CalcularSaldo();
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro ao carregar financeiro: {ex.Message}");
            }
        }

        private void DistribuirListas(List<FinanceiroRegistro> lista)
        {
            ContasPendentes.Clear();
            ExtratoGeral.Clear();

            var ordenados = lista.OrderBy(x => x.DataVencimento).ToList();

            foreach (var item in ordenados)
            {
                item.StatusColor = CalcularCorStatus(item.DataVencimento);
                
                item.DescricaoDisplay = item.TotalParcelas > 1
                    ? $"{item.Descricao} ({item.ParcelaAtual}/{item.TotalParcelas})"
                    : item.Descricao;

                if (!item.FoiPago)
                {
                    ContasPendentes.Add(item);
                    if (item.Tipo == "Saida") { _ = DispararAlertaSeguro(item); }
                }
                else
                {
                    ExtratoGeral.Add(item);
                }
            }
        }

        private async Task DispararAlertaSeguro(FinanceiroRegistro conta)
        {
            if (_notificationManager == null || conta == null || string.IsNullOrEmpty(conta.Id)) return;

            try
            {
                var hoje = DateTime.Today;
                var vencimento = conta.DataVencimento.Date;
                var diasRestantes = (vencimento - hoje).TotalDays;

                if (diasRestantes > 4) return;

                int baseId = conta.Id.GetHashCode() & 0x3FFFFFFF; 

                // Alerta 1: Manhã (08:30)
                DateTime horarioManha = vencimento.AddHours(8).AddMinutes(30);
                await ProcessarEnvioIndividual(baseId + 100, horarioManha, conta, diasRestantes);

                // Alerta 2: Tarde (17:00)
                DateTime horarioTarde = vencimento.AddHours(17).AddMinutes(0);
                await ProcessarEnvioIndividual(baseId + 200, horarioTarde, conta, diasRestantes);
            }
            catch (Exception ex) { Debug.WriteLine($"Erro Alerta: {ex.Message}"); }
        }

        private async Task ProcessarEnvioIndividual(int id, DateTime dataAgendada, FinanceiroRegistro conta, double diasRestantes)
        {
            if (_notificationManager == null || conta == null) return;

            var notification = new Notification
            {
                Id = id,
                Title = diasRestantes < 0 ? "🚨 CONTA VENCIDA!" : "⚠️ LEMBRETE DE PAGAMENTO",
                Message = $"{conta.Descricao} no valor de {conta.Valor:C} (Vence: {conta.DataVencimento:dd/MM})",
                BadgeCount = 1,
                Channel = "CentralAlerta"
            };

            if (dataAgendada < DateTime.Now)
            {
                if (conta.DataVencimento.Date <= DateTime.Today)
                {
                     await _notificationManager.Send(notification);
                }
            }
            else
            {
                notification.ScheduleDate = dataAgendada;
                await _notificationManager.Send(notification);
            }
        }

        // MÉTODO RESTAURADO PARA CORRIGIR O ERRO CS1061
        public void OrdenarLista(string criterio)
        {
            List<FinanceiroRegistro> ordenado = criterio switch
            {
                "Vencimento" => _todasAsContas.OrderBy(x => x.DataVencimento).ToList(),
                "Maior Valor" => _todasAsContas.OrderByDescending(x => x.Valor).ToList(),
                "Menor Valor" => _todasAsContas.OrderBy(x => x.Valor).ToList(),
                _ => _todasAsContas.ToList()
            };
            DistribuirListas(ordenado);
        }

        [RelayCommand]
        public async Task ConfirmarPagamento(FinanceiroRegistro registro)
        {
            if (registro == null || string.IsNullOrEmpty(registro.Id)) return;

            bool confirmar = await Shell.Current.DisplayAlert("Confirmar", $"Pagar '{registro.Descricao}'?", "Sim", "Não");
            if (!confirmar) return;

            if (_notificationManager != null)
            {
                int baseId = registro.Id.GetHashCode() & 0x3FFFFFFF;
                try { 
                    await _notificationManager.Cancel(baseId + 100); 
                    await _notificationManager.Cancel(baseId + 200); 
                } catch { }
            }

            var historico = new FinanceiroRegistro
            {
                Id = Guid.NewGuid().ToString(),
                Descricao = registro.TotalParcelas > 1 
                    ? $"{registro.Descricao} ({registro.ParcelaAtual}/{registro.TotalParcelas})"
                    : registro.Descricao,
                Valor = registro.Valor,
                Tipo = registro.Tipo,
                DataVencimento = registro.DataVencimento,
                FoiPago = true
            };
            await _dbService.SaveItemAsync(historico);
            _ = _firebaseService.SaveFinanceiroAsync(historico);

            if (registro.TotalParcelas > 1 && registro.ParcelaAtual < registro.TotalParcelas)
            {
                registro.ParcelaAtual++;
                registro.DataVencimento = registro.DataVencimento.AddMonths(1);
                registro.FoiPago = false; 
            }
            else if (registro.IsFixo)
            {
                registro.DataVencimento = registro.DataVencimento.AddMonths(1);
                registro.FoiPago = false;
            }
            else
            {
                registro.FoiPago = true;
            }

            await _dbService.SaveItemAsync(registro);
            _ = _firebaseService.SaveFinanceiroAsync(registro);
            await CarregarDados();
        }

        [RelayCommand]
        public async Task ExcluirRegistro(FinanceiroRegistro registro)
        {
            if (registro == null || string.IsNullOrEmpty(registro.Id)) return;
            
            bool confirmar = await Shell.Current.DisplayAlert("Excluir", $"Excluir '{registro.Descricao}'?", "Sim", "Não");
            if (!confirmar) return;

            if (_notificationManager != null)
            {
                int baseId = registro.Id.GetHashCode() & 0x3FFFFFFF;
                try { 
                    await _notificationManager.Cancel(baseId + 100); 
                    await _notificationManager.Cancel(baseId + 200); 
                } catch { }
            }

            await _dbService.DeleteItemAsync(registro);
            _ = _firebaseService.DeleteFinanceiroAsync(registro.Id ?? string.Empty);
            await CarregarDados();
        }

        private async Task SalvarRegistroFull(FinanceiroRegistro reg)
        {
            await _dbService.SaveItemAsync(reg);
            if (reg.Tipo == "Saida" && !reg.FoiPago) 
            { 
                await DispararAlertaSeguro(reg); 
            }
            try { await _firebaseService.SaveFinanceiroAsync(reg); } catch { }
        }

        [RelayCommand]
        public async Task AbrirCadastro()
        {
            var popup = new CadastroFinanceiroPopup();
            var resultado = await Shell.Current.ShowPopupAsync(popup);
            if (resultado is FinanceiroRegistro novo) { await SalvarRegistroFull(novo); await CarregarDados(); }
        }

        [RelayCommand]
        public async Task AbrirLancamentoExtrato()
        {
            var popup = new CadastroFinanceiroPopup(null, true);
            var resultado = await Shell.Current.ShowPopupAsync(popup);
            if (resultado is FinanceiroRegistro novo) { await SalvarRegistroFull(novo); await CarregarDados(); }
        }

        [RelayCommand]
        public async Task EditarRegistro(FinanceiroRegistro registro)
        {
            if (registro == null) return;
            var popup = new CadastroFinanceiroPopup(registro);
            var resultado = await Shell.Current.ShowPopupAsync(popup);
            if (resultado is FinanceiroRegistro editado) { await SalvarRegistroFull(editado); await CarregarDados(); }
        }

        [RelayCommand]
        public void Filtrar(string texto)
        {
            if (string.IsNullOrWhiteSpace(texto)) { DistribuirListas(_todasAsContas); return; }
            var filtrados = _todasAsContas.Where(x => (x.Descricao ?? "").ToLower().Contains(texto.ToLower())).ToList();
            DistribuirListas(filtrados);
        }

        private void CalcularSaldo()
        {
            var entradas = _todasAsContas.Where(x => x.FoiPago && x.Tipo == "Entrada").Sum(x => x.Valor);
            var saidas = _todasAsContas.Where(x => x.FoiPago && x.Tipo == "Saida").Sum(x => x.Valor);
            SaldoTotal = entradas - saidas;
        }

        private Color CalcularCorStatus(DateTime vencimento)
        {
            var hoje = DateTime.Today;
            if (vencimento.Date < hoje) return Color.FromArgb("#FF0000");
            if (vencimento.Date == hoje || (vencimento - hoje).TotalDays <= 4) return Color.FromArgb("#FFD700");
            return Color.FromArgb("#008000");
        }
    }
}