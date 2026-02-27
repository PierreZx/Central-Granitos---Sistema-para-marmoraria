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
        private ObservableCollection<FinanceiroRegistro> orcamentosPendentes = new();

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

                // Busca local e atualiza a lista interna
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
            OrcamentosPendentes.Clear();

            var ordenados = lista.OrderBy(x => x.DataVencimento).ToList();

            foreach (var item in ordenados)
            {
                // LÓGICA DE CORES (SEMÁFORO):
                item.StatusColor = CalcularCorStatus(item.DataVencimento);
                
                string descSegura = item.Descricao ?? "Sem Descrição";

                // EXIBIÇÃO DE PARCELAS (0/5, 1/5 etc):
                if (item.IsParcelado || item.TotalParcelas > 1)
                {
                    item.DescricaoDisplay = $"{descSegura} ({item.ParcelaAtual}/{item.TotalParcelas})";
                }
                else
                {
                    item.DescricaoDisplay = descSegura;
                }

                if (!item.FoiPago)
                {
                    // LÓGICA DE DISTRIBUIÇÃO: Separa orçamentos de contas normais
                    if (!string.IsNullOrEmpty(item.Descricao) && item.Descricao.StartsWith("Orçamento:"))
                    {
                        OrcamentosPendentes.Add(item);
                    }
                    else
                    {
                        ContasPendentes.Add(item);
                        // Alerta apenas para saídas (contas a pagar)
                        if (item.Tipo == "Saida") { _ = DispararAlertaSeguro(item); }
                    }
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

                DateTime horarioManha = vencimento.AddHours(8).AddMinutes(30);
                await ProcessarEnvioIndividual(baseId + 100, horarioManha, conta, diasRestantes);

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
                Message = $"{(conta.Descricao ?? "Conta")} no valor de {conta.Valor:C} (Vence: {conta.DataVencimento:dd/MM})",
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

            bool confirmar = await Shell.Current.DisplayAlert("Confirmar", $"Registrar pagamento de '{registro.DescricaoDisplay}'?", "Sim", "Não");
            if (!confirmar) return;

            if (_notificationManager != null)
            {
                int baseId = registro.Id.GetHashCode() & 0x3FFFFFFF;
                try { 
                    await _notificationManager.Cancel(baseId + 100); 
                    await _notificationManager.Cancel(baseId + 200); 
                } catch { }
            }

            string descricaoParaHistorico = registro.Descricao ?? "Lançamento";

            // Gera o registro no extrato (dinheiro entra/sai de verdade agora)
            var historico = new FinanceiroRegistro
            {
                Id = Guid.NewGuid().ToString(),
                Descricao = registro.TotalParcelas > 1 
                    ? $"{descricaoParaHistorico} ({registro.ParcelaAtual}/{registro.TotalParcelas})"
                    : descricaoParaHistorico,
                Valor = registro.Valor,
                Tipo = registro.Tipo,
                DataVencimento = DateTime.Now, 
                FoiPago = true
            };
            await _dbService.SaveItemAsync(historico);
            _ = _firebaseService.SaveFinanceiroAsync(historico);

            // GERENCIAMENTO DE PARCELAS E RECORRÊNCIA:
            if (registro.IsParcelado && registro.ParcelaAtual < registro.TotalParcelas)
            {
                registro.ParcelaAtual++;
                registro.DataVencimento = registro.DataVencimento.AddMonths(1);
                registro.FoiPago = false; // Continua pendente para a próxima parcela
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
            
            bool confirmar = await Shell.Current.DisplayAlert("Excluir", $"Excluir '{registro.Descricao ?? "esta conta"}'?", "Sim", "Não");
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
            _ = _firebaseService.DeleteFinanceiroAsync(registro.Id);
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
            var diasParaVencer = (vencimento.Date - hoje).TotalDays;

            if (vencimento.Date < hoje) 
                return Color.FromArgb("#FF0000"); // VERMELHO: Vencido ou hoje atrasado

            if (diasParaVencer <= 3) 
                return Color.FromArgb("#FFD700"); // AMARELO: Entre hoje e 3 dias (Perto)

            return Color.FromArgb("#008000"); // VERDE: Mais de 3 dias para o vencimento
        }
    }
}