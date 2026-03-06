using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using Marmorariacentral.Views.Financeiro;
using System.Collections.ObjectModel;
using System.Diagnostics;
using Shiny.Notifications;
using Google.Cloud.Firestore;

#pragma warning disable CA1416 

namespace Marmorariacentral.ViewModels
{
    public partial class FinanceiroViewModel : ObservableObject, IDisposable
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;
        private readonly INotificationManager? _notificationManager;
        
        // CORREÇÃO DO ERRO CS0029: Usando o tipo exato do Firestore
        private FirestoreChangeListener? _listenerRegistration;

        private List<FinanceiroRegistro> _todasAsContas = new();

        [ObservableProperty] private ObservableCollection<FinanceiroRegistro> contasPendentes = new();
        [ObservableProperty] private ObservableCollection<FinanceiroRegistro> extratoGeral = new();
        [ObservableProperty] private ObservableCollection<FinanceiroRegistro> orcamentosPendentes = new();
        [ObservableProperty] private double saldoTotal;

        public FinanceiroViewModel(DatabaseService dbService, FirebaseService firebaseService, INotificationManager? notificationManager = null)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            _notificationManager = notificationManager;
            
            _ = IniciarSincronizacaoRealtime();
        }

        private async Task IniciarSincronizacaoRealtime()
        {
            try
            {
                var db = await _firebaseService.GetFirestoreDb();
                var collection = db.Collection("financeiro"); 

                _listenerRegistration = collection.Listen(snapshot =>
                {
                    MainThread.BeginInvokeOnMainThread(async () =>
                    {
                        foreach (var doc in snapshot.Documents)
                        {
                            if (doc.Exists)
                            {
                                var registro = doc.ConvertTo<FinanceiroRegistro>();
                                registro.Id = doc.Id;

                                // TRAVA ANTI-DUPLICIDADE: Atualiza se já existir, adiciona se for novo
                                var existente = _todasAsContas.FirstOrDefault(x => x.Id == registro.Id);
                                if (existente != null)
                                {
                                    int index = _todasAsContas.IndexOf(existente);
                                    _todasAsContas[index] = registro;
                                }
                                else
                                {
                                    _todasAsContas.Add(registro);
                                }
                                
                                // Sincroniza banco local
                                _ = _dbService.SaveItemAsync(registro);
                            }
                        }

                        DistribuirListas(_todasAsContas);
                        CalcularSaldo();
                    });
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro no Realtime: {ex.Message}");
                await CarregarDados(); 
            }
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
                
                // Agrupa por ID para garantir que não haja duplicatas vindas do SQLite
                _todasAsContas = lista?.GroupBy(x => x.Id).Select(g => g.First()).ToList() ?? new List<FinanceiroRegistro>();

                MainThread.BeginInvokeOnMainThread(() =>
                {
                    DistribuirListas(_todasAsContas);
                    CalcularSaldo();
                });
            }
            catch (Exception ex) { Debug.WriteLine($"Erro: {ex.Message}"); }
        }

        private void DistribuirListas(List<FinanceiroRegistro> lista)
        {
            ContasPendentes.Clear();
            ExtratoGeral.Clear();
            OrcamentosPendentes.Clear();

            var ordenados = lista.OrderBy(x => x.DataVencimento).ToList();

            foreach (var item in ordenados)
            {
                item.StatusColor = CalcularCorStatus(item.DataVencimento);
                string descSegura = item.Descricao ?? "Sem Descrição";

                if (item.TotalParcelas > 1)
                    item.DescricaoDisplay = $"{descSegura} ({item.ParcelaAtual}/{item.TotalParcelas})";
                else
                    item.DescricaoDisplay = descSegura;

                if (!item.FoiPago)
                {
                    if (!string.IsNullOrEmpty(item.Descricao) && item.Descricao.StartsWith("Orçamento:"))
                        OrcamentosPendentes.Add(item);
                    else
                    {
                        ContasPendentes.Add(item);
                        if (item.Tipo == "Saida") { _ = DispararAlertaSeguro(item); }
                    }
                }
                else
                {
                    ExtratoGeral.Add(item);
                }
            }
        }

        [RelayCommand]
        public async Task ConfirmarPagamento(FinanceiroRegistro registro)
        {
            if (registro == null || string.IsNullOrEmpty(registro.Id)) return;

            bool confirmar = await Shell.Current.DisplayAlert("Pagamento", 
                $"Tem certeza que quer pagar '{registro.DescricaoDisplay}'?", "Sim", "Cancelar");
            
            if (!confirmar) 
            {
                await CarregarDados(); 
                return;
            }

            if (_notificationManager != null)
            {
                int baseId = registro.Id.GetHashCode() & 0x3FFFFFFF;
                try { await _notificationManager.Cancel(baseId + 100); } catch { }
            }

            if (registro.IsFixo || (registro.TotalParcelas > 1))
            {
                var comprovante = new FinanceiroRegistro
                {
                    Id = Guid.NewGuid().ToString(),
                    Descricao = registro.TotalParcelas > 1 
                                ? $"{registro.Descricao} (Paga Parc. {registro.ParcelaAtual})" 
                                : $"{registro.Descricao} (Paga {DateTime.Now:MM/yyyy})",
                    Valor = registro.Valor,
                    Tipo = registro.Tipo,
                    DataVencimento = DateTime.Now,
                    FoiPago = true 
                };
                await _dbService.SaveItemAsync(comprovante);
                await _firebaseService.SaveFinanceiroAsync(comprovante);

                if (registro.TotalParcelas > 1 && registro.ParcelaAtual < registro.TotalParcelas)
                {
                    registro.ParcelaAtual++;
                    registro.DataVencimento = registro.DataVencimento.AddMonths(1);
                }
                else if (registro.IsFixo)
                {
                    registro.DataVencimento = registro.DataVencimento.AddMonths(1);
                }
                else { registro.FoiPago = true; }
            }
            else { registro.FoiPago = true; }

            await _dbService.SaveItemAsync(registro);
            await _firebaseService.SaveFinanceiroAsync(registro);

            await CarregarDados();
            
            CalcularSaldo();
        }

        [RelayCommand]
        public async Task ExcluirRegistro(FinanceiroRegistro registro)
        {
            if (registro == null || string.IsNullOrEmpty(registro.Id)) return;

            bool confirmar = await Shell.Current.DisplayAlert("Excluir", 
                $"Tem certeza que deseja EXCLUIR '{registro.Descricao}'?", "Excluir", "Cancelar");
            
            if (!confirmar) return;

            try 
            {
                await _firebaseService.DeleteFinanceiroAsync(registro.Id);
                await _dbService.DeleteItemAsync(registro);

                if (_notificationManager != null)
                {
                    int baseId = registro.Id.GetHashCode() & 0x3FFFFFFF;
                    await _notificationManager.Cancel(baseId + 100);
                }
                
                MainThread.BeginInvokeOnMainThread(() => {
                    _todasAsContas.RemoveAll(x => x.Id == registro.Id);
                    DistribuirListas(_todasAsContas);
                    CalcularSaldo();
                });
            }
            catch (Exception ex) { Debug.WriteLine($"Erro na exclusão: {ex.Message}"); }
        }

        private async Task<string?> SalvarOuAtualizarRegistro(FinanceiroRegistro novo)
        {
            try 
            {
                bool isEdicao = _todasAsContas.Any(x => x.Id == novo.Id);

                if (!isEdicao)
                {
                    if (string.IsNullOrEmpty(novo.Id)) novo.Id = Guid.NewGuid().ToString();
                    
                    var duplicado = _todasAsContas.FirstOrDefault(x => 
                        x.Descricao?.Trim().ToLower() == novo.Descricao?.Trim().ToLower() && 
                        Math.Abs(x.Valor - novo.Valor) < 0.001 &&
                        x.DataVencimento.Date == novo.DataVencimento.Date);

                    if (duplicado != null) return "Este registro já existe!";
                }

                await _dbService.SaveItemAsync(novo);
                await _firebaseService.SaveFinanceiroAsync(novo);

                var existente = _todasAsContas.FirstOrDefault(x => x.Id == novo.Id);
                if (existente != null) _todasAsContas[_todasAsContas.IndexOf(existente)] = novo;
                else _todasAsContas.Add(novo);

                DistribuirListas(_todasAsContas);
                return null; 
            }
            catch (Exception ex) { return $"Erro: {ex.Message}"; }
        }

        [RelayCommand]
        public async Task AbrirCadastro()
        {
            var resultado = await Shell.Current.ShowPopupAsync(new CadastroFinanceiroPopup());
            if (resultado is FinanceiroRegistro novo) 
            { 
                var erro = await SalvarOuAtualizarRegistro(novo); 
                if (Shell.Current.CurrentPage is FinanceiroPage page) await page.MostrarFeedback(erro == null, erro ?? "Salvo com sucesso!");
            }
        }

        [RelayCommand]
        public async Task AbrirLancamentoExtrato()
        {
            var resultado = await Shell.Current.ShowPopupAsync(new CadastroFinanceiroPopup(null, true));
            if (resultado is FinanceiroRegistro novo) 
            { 
                novo.FoiPago = true;
                var erro = await SalvarOuAtualizarRegistro(novo); 
                if (Shell.Current.CurrentPage is FinanceiroPage page) await page.MostrarFeedback(erro == null, erro ?? "Lançado!");
            }
        }

        [RelayCommand]
        public async Task EditarRegistro(FinanceiroRegistro registro)
        {
            if (registro == null) return;
            var resultado = await Shell.Current.ShowPopupAsync(new CadastroFinanceiroPopup(registro));
            if (resultado is FinanceiroRegistro editado) 
            { 
                var erro = await SalvarOuAtualizarRegistro(editado); 
                if (Shell.Current.CurrentPage is FinanceiroPage page) await page.MostrarFeedback(erro == null, erro ?? "Alterado!");
            }
        }

        [RelayCommand]
        public void Filtrar(string texto)
        {
            if (string.IsNullOrWhiteSpace(texto)) { DistribuirListas(_todasAsContas); return; }
            DistribuirListas(_todasAsContas.Where(x => (x.Descricao ?? "").ToLower().Contains(texto.ToLower())).ToList());
        }

        private void CalcularSaldo()
        {
            SaldoTotal = _todasAsContas.Where(x => x.FoiPago && x.Tipo == "Entrada").Sum(x => x.Valor) - 
                         _todasAsContas.Where(x => x.FoiPago && x.Tipo == "Saida").Sum(x => x.Valor);
        }

        private Color CalcularCorStatus(DateTime vencimento)
        {
            var hoje = DateTime.Today;
            if (vencimento.Date < hoje) return Color.FromArgb("#FF0000"); 
            if ((vencimento.Date - hoje).TotalDays <= 3) return Color.FromArgb("#FFD700"); 
            return Color.FromArgb("#008000"); 
        }

        private async Task DispararAlertaSeguro(FinanceiroRegistro conta)
        {
            if (_notificationManager == null || conta == null) return;
            try {
                var dias = (conta.DataVencimento.Date - DateTime.Today).TotalDays;
                if (dias > 4) return;
                int baseId = conta.Id.GetHashCode() & 0x3FFFFFFF; 
                await ProcessarEnvioIndividual(baseId + 100, conta.DataVencimento.Date.AddHours(8), conta, dias);
            } catch { }
        }

        private async Task ProcessarEnvioIndividual(int id, DateTime data, FinanceiroRegistro c, double d)
        {
            if (_notificationManager == null) return;
            var n = new Notification { 
                Id = id, Title = d < 0 ? "🚨 CONTA VENCIDA!" : "⚠️ LEMBRETE CENTRAL", 
                Message = $"{c.Descricao}: {c.Valor:C}", Channel = "CentralAlerta" 
            };
            if (data < DateTime.Now) { if (c.DataVencimento.Date <= DateTime.Today) await _notificationManager.Send(n); }
            else { n.ScheduleDate = data; await _notificationManager.Send(n); }
        }

        public void OrdenarLista(string crit)
        {
            _todasAsContas = crit switch {
                "Vencimento" => _todasAsContas.OrderBy(x => x.DataVencimento).ToList(),
                "Maior Valor" => _todasAsContas.OrderByDescending(x => x.Valor).ToList(),
                "Menor Valor" => _todasAsContas.OrderBy(x => x.Valor).ToList(),
                _ => _todasAsContas
            };
            DistribuirListas(_todasAsContas);
        }

        public void Dispose()
        {
            // CORREÇÃO: O listener do Firestore é encerrado via StopAsync()
            _ = Task.Run(async () => {
                if (_listenerRegistration != null)
                {
                    await _listenerRegistration.StopAsync();
                }
            });
        }
    }
}