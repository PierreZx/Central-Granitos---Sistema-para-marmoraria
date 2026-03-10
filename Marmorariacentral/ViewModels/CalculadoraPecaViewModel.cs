using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using Marmorariacentral.Drawables;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Globalization;
using Microsoft.Maui.Graphics;
using SkiaSharp;

namespace Marmorariacentral.ViewModels
{
    [QueryProperty(nameof(ClienteSelecionado), "ClienteSelecionado")]
    [QueryProperty(nameof(PecaParaEditar), "PecaParaEditar")]
    public partial class CalculadoraPecaViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;
        private readonly PdfService _pdfService;

        // ==========================================
        // OBJETOS DE DADOS E ESTADO
        // ==========================================
        [ObservableProperty] private Cliente? clienteSelecionado;
        [ObservableProperty] private PecaOrcamento peca = new();
        [ObservableProperty] private PecaOrcamento pecaParaEditar;

        [ObservableProperty] private ObservableCollection<EstoqueItem> listaEstoque = new();
        [ObservableProperty] private EstoqueItem? pedraSelecionada;
        [ObservableProperty] private double valorMaoDeObra;
        [ObservableProperty] private double totalGeral;
        
        [ObservableProperty] private string ladoP2 = "Esquerda";
        [ObservableProperty] private string ladoP3 = "Direita";
        public List<string> LadosDisponiveis { get; } = new() { "Esquerda", "Direita" };
        public List<string> PecasDisponiveis { get; } = new() { "P1", "P2", "P3" };

        // INPUTS DE TEXTO
        [ObservableProperty] private string larguraInput = "0,00";
        [ObservableProperty] private string alturaInput = "0,00";
        [ObservableProperty] private string larguraP2Input = "0,00";
        [ObservableProperty] private string alturaP2Input = "0,00";
        [ObservableProperty] private string larguraP3Input = "0,00";
        [ObservableProperty] private string alturaP3Input = "0,00";
        [ObservableProperty] private string valorMetroLinearInput = "130,00";
        [ObservableProperty] private string quantidadeInput = "1";
        [ObservableProperty] private bool usarMultiplicador = false;

        partial void OnLarguraInputChanged(string value) { Peca.Largura = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnAlturaInputChanged(string value) { Peca.Altura = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnLarguraP2InputChanged(string value) { Peca.LarguraP2 = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnAlturaP2InputChanged(string value) { Peca.AlturaP2 = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnLarguraP3InputChanged(string value) { Peca.LarguraP3 = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnAlturaP3InputChanged(string value) { Peca.AlturaP3 = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnValorMetroLinearInputChanged(string value) { Peca.ValorMetroLinear = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnQuantidadeInputChanged(string value) => NotificarMudanca();
        partial void OnPedraSelecionadaChanged(EstoqueItem? value) => NotificarMudanca();
        partial void OnBojoXInputChanged(string value) => NotificarMudanca();
        partial void OnBojoYInputChanged(string value) => NotificarMudanca();
        partial void OnCooktopXInputChanged(string value) => NotificarMudanca();
        partial void OnCooktopYInputChanged(string value) => NotificarMudanca();
        partial void OnLarguraBojoInputChanged(string value) => NotificarMudanca();
        partial void OnAlturaBojoInputChanged(string value) => NotificarMudanca();
        partial void OnLarguraCooktopInputChanged(string value) => NotificarMudanca();
        partial void OnAlturaCooktopInputChanged(string value) => NotificarMudanca();

        public int Quantidade => int.TryParse(QuantidadeInput, out int q) ? Math.Max(q, 1) : 1;
        public double ValorTotalPeca => TotalGeral;

        // RECORTES
        [ObservableProperty] private bool temBojo = false;
        [ObservableProperty] private string pecaDestinoBojo = "P1";
        [ObservableProperty] private string larguraBojoInput = "0,60";
        [ObservableProperty] private string alturaBojoInput = "0,40";
        [ObservableProperty] private string bojoXInput = "0,50";
        [ObservableProperty] private string bojoYInput = "0,30";
        [ObservableProperty] private bool temCooktop = false;
        [ObservableProperty] private string pecaDestinoCooktop = "P1";
        [ObservableProperty] private string larguraCooktopInput = "0,55";
        [ObservableProperty] private string alturaCooktopInput = "0,45";
        [ObservableProperty] private string cooktopXInput = "1,50";
        [ObservableProperty] private string cooktopYInput = "1,30";

        // RODOBANCA
        [ObservableProperty] private double rodobancaP1Esquerda = 0.00;
        [ObservableProperty] private double rodobancaP1Direita = 0.00;
        [ObservableProperty] private double rodobancaP1Frente = 0.00;
        [ObservableProperty] private double rodobancaP1Tras = 0.00;
        [ObservableProperty] private double rodobancaP2Esquerda = 0.00;
        [ObservableProperty] private double rodobancaP2Direita = 0.00;
        [ObservableProperty] private double rodobancaP2Frente = 0.00;
        [ObservableProperty] private double rodobancaP2Tras = 0.00;
        [ObservableProperty] private double rodobancaP3Esquerda = 0.00;
        [ObservableProperty] private double rodobancaP3Direita = 0.00;
        [ObservableProperty] private double rodobancaP3Frente = 0.00;
        [ObservableProperty] private double rodobancaP3Tras = 0.00;

        // SAIA
        [ObservableProperty] private double saiaP1Esquerda = 0.00;
        [ObservableProperty] private double saiaP1Direita = 0.00;
        [ObservableProperty] private double saiaP1Frente = 0.00;
        [ObservableProperty] private double saiaP1Tras = 0.00;
        [ObservableProperty] private double saiaP2Esquerda = 0.00;
        [ObservableProperty] private double saiaP2Direita = 0.00;
        [ObservableProperty] private double saiaP2Frente = 0.00;
        [ObservableProperty] private double saiaP2Tras = 0.00;
        [ObservableProperty] private double saiaP3Esquerda = 0.00;
        [ObservableProperty] private double saiaP3Direita = 0.00;
        [ObservableProperty] private double saiaP3Frente = 0.00;
        [ObservableProperty] private double saiaP3Tras = 0.00;

        public bool TemPernaEsquerda => Peca.LarguraP2 > 0.01 && LadoP2 == "Esquerda";
        public bool TemPernaDireita => (Peca.LarguraP2 > 0.01 && LadoP2 == "Direita") || (Peca.LarguraP3 > 0.01);
        
        // Alterado para object para evitar erro de conversão
        public IDrawable DesenhoPeca { get; }

        public CalculadoraPecaViewModel(DatabaseService dbService, PdfService pdfService)
        {
            _dbService = dbService;
            _pdfService = pdfService;

            DesenhoPeca = new PecaDrawable(this);

            _ = CarregarEstoque();
        }

        [RelayCommand]
        public async Task GerarDocumentoTecnicoAsync(View viewParaCapturar) 
        {
            if (ClienteSelecionado == null) return;
            try
            {
                // Corrigido: passar os parâmetros corretos para o método
                await _pdfService.GerarPdfTecnicoAsync(ClienteSelecionado, 
                    new List<PecaOrcamento> { Peca }, 
                    viewParaCapturar);
            }
            catch (Exception ex) { Debug.WriteLine($"Erro PDF técnico: {ex.Message}"); }
        }

        [RelayCommand]
        public async Task GerarOrcamentoClienteAsync(View viewParaCapturar) 
        {
            if (ClienteSelecionado == null) return;
            try
            {
                // Corrigido: passar os parâmetros corretos para o método
                await _pdfService.GerarPdfClienteAsync(ClienteSelecionado, 
                    new List<PecaOrcamento> { Peca }, 
                    viewParaCapturar);
            }
            catch (Exception ex) { Debug.WriteLine($"Erro PDF cliente: {ex.Message}"); }
        }

        [RelayCommand]
        public void NotificarMudanca()
        {
            CalcularTotal();
            MainThread.BeginInvokeOnMainThread(() =>
            {
                OnPropertyChanged(nameof(DesenhoPeca));
                OnPropertyChanged(nameof(TemPernaEsquerda));
                OnPropertyChanged(nameof(TemPernaDireita));
                OnPropertyChanged(nameof(TotalGeral));
                OnPropertyChanged(nameof(ValorTotalPeca));
            });
        }

        private double ConverterParaDouble(string valor)
        {
            if (string.IsNullOrWhiteSpace(valor))
                return 0;

            valor = valor.Replace(",", ".");

            return double.TryParse(
                valor,
                NumberStyles.Any,
                CultureInfo.InvariantCulture,
                out double result
            ) ? result : 0;
        }

        private void CalcularTotal()
        {
            if (PedraSelecionada == null)
            {
                TotalGeral = 0;
                return;
            }

            double areaTotal =
                (Peca.Largura * Peca.Altura) +
                (Peca.LarguraP2 * Peca.AlturaP2) +
                (Peca.LarguraP3 * Peca.AlturaP3);

            double metrosLineares =
                Peca.Largura +
                (Peca.LarguraP2 > 0.01 ? Peca.LarguraP2 : 0) +
                (Peca.LarguraP3 > 0.01 ? Peca.LarguraP3 : 0);

            double custoMaterial = areaTotal * PedraSelecionada.ValorPorMetro;

            // Verifica se existe algum acabamento
            bool temAcabamento =
                RodobancaP1Esquerda > 0 || RodobancaP1Direita > 0 || RodobancaP1Frente > 0 || RodobancaP1Tras > 0 ||
                RodobancaP2Esquerda > 0 || RodobancaP2Direita > 0 || RodobancaP2Frente > 0 || RodobancaP2Tras > 0 ||
                RodobancaP3Esquerda > 0 || RodobancaP3Direita > 0 || RodobancaP3Frente > 0 || RodobancaP3Tras > 0 ||

                SaiaP1Esquerda > 0 || SaiaP1Direita > 0 || SaiaP1Frente > 0 || SaiaP1Tras > 0 ||
                SaiaP2Esquerda > 0 || SaiaP2Direita > 0 || SaiaP2Frente > 0 || SaiaP2Tras > 0 ||
                SaiaP3Esquerda > 0 || SaiaP3Direita > 0 || SaiaP3Frente > 0 || SaiaP3Tras > 0;

            double custoMaoObra = 0;

            if (temAcabamento)
            {
                custoMaoObra = metrosLineares * ConverterParaDouble(ValorMetroLinearInput);
            }

            TotalGeral = (custoMaterial + custoMaoObra) * Quantidade;
        }

        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(IsAbaPrincipalVisible))]
        [NotifyPropertyChangedFor(nameof(IsAbaRodobancaVisible))]
        [NotifyPropertyChangedFor(nameof(IsAbaSaiaVisible))]
        [NotifyPropertyChangedFor(nameof(IsAbaRecortesVisible))]
        private string abaAtiva = "Principal";

        public bool IsAbaPrincipalVisible => AbaAtiva == "Principal";
        public bool IsAbaRodobancaVisible => AbaAtiva == "Rodobanca";
        public bool IsAbaSaiaVisible => AbaAtiva == "Saia";
        public bool IsAbaRecortesVisible => AbaAtiva == "Recortes";

        [RelayCommand] private void MostrarAbaPrincipal() => AbaAtiva = "Principal";
        [RelayCommand] private void MostrarAbaRodobanca() => AbaAtiva = "Rodobanca";
        [RelayCommand] private void MostrarAbaSaia() => AbaAtiva = "Saia";
        [RelayCommand] private void MostrarAbaRecortes() => AbaAtiva = "Recortes";

        public async void ApplyQueryAttributes(IDictionary<string, object> query)
        {
            if (query.TryGetValue("PecaParaEditar", out var pecaObj) && pecaObj is PecaOrcamento edicao)
            {
                if (ListaEstoque.Count == 0) await CarregarEstoque();
                Peca = edicao;
                if (!string.IsNullOrEmpty(edicao.PedraNome))
                    PedraSelecionada = ListaEstoque.FirstOrDefault(p => p.NomeChapa == edicao.PedraNome);

                LarguraInput = edicao.Largura.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                AlturaInput = edicao.Altura.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                LarguraP2Input = edicao.LarguraP2.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                AlturaP2Input = edicao.AlturaP2.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                LadoP2 = edicao.LadoP2 ?? "Esquerda";
                LarguraP3Input = edicao.LarguraP3.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                AlturaP3Input = edicao.AlturaP3.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                LadoP3 = edicao.LadoP3 ?? "Direita";
                ValorMetroLinearInput = edicao.ValorMetroLinear.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                QuantidadeInput = edicao.Quantidade.ToString();
                UsarMultiplicador = edicao.UsarMultiplicador;

                RodobancaP1Esquerda = edicao.RodobancaP1Esquerda; RodobancaP1Direita = edicao.RodobancaP1Direita;
                RodobancaP1Frente = edicao.RodobancaP1Frente; RodobancaP1Tras = edicao.RodobancaP1Tras;
                RodobancaP2Esquerda = edicao.RodobancaP2Esquerda; RodobancaP2Direita = edicao.RodobancaP2Direita;
                RodobancaP2Frente = edicao.RodobancaP2Frente; RodobancaP2Tras = edicao.RodobancaP2Tras;
                RodobancaP3Esquerda = edicao.RodobancaP3Esquerda; RodobancaP3Direita = edicao.RodobancaP3Direita;
                RodobancaP3Frente = edicao.RodobancaP3Frente; RodobancaP3Tras = edicao.RodobancaP3Tras;

                SaiaP1Esquerda = edicao.SaiaP1Esquerda; SaiaP1Direita = edicao.SaiaP1Direita;
                SaiaP1Frente = edicao.SaiaP1Frente; SaiaP1Tras = edicao.SaiaP1Tras;
                SaiaP2Esquerda = edicao.SaiaP2Esquerda; SaiaP2Direita = edicao.SaiaP2Direita;
                SaiaP2Frente = edicao.SaiaP2Frente; SaiaP2Tras = edicao.SaiaP2Tras;
                SaiaP3Esquerda = edicao.SaiaP3Esquerda; SaiaP3Direita = edicao.SaiaP3Direita;
                SaiaP3Frente = edicao.SaiaP3Frente; SaiaP3Tras = edicao.SaiaP3Tras;

                TemBojo = edicao.TemBojo; PecaDestinoBojo = edicao.PecaDestinoBojo ?? "P1";
                LarguraBojoInput = edicao.LarguraBojo.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                AlturaBojoInput = edicao.AlturaBojo.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                BojoXInput = edicao.BojoX.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                BojoYInput = edicao.BojoY.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                TemCooktop = edicao.TemCooktop; PecaDestinoCooktop = edicao.PecaDestinoCooktop ?? "P1";
                LarguraCooktopInput = edicao.LarguraCooktop.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                AlturaCooktopInput = edicao.AlturaCooktop.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                CooktopXInput = edicao.CooktopX.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));
                CooktopYInput = edicao.CooktopY.ToString("F2", CultureInfo.GetCultureInfo("pt-BR"));

                await Task.Delay(150);
                NotificarMudanca();
            }
        }

        [RelayCommand]
        private async Task SalvarPeca()
        {
            if (PedraSelecionada == null) return;
            Peca.PedraNome = PedraSelecionada.NomeChapa; Peca.ValorM2 = PedraSelecionada.ValorPorMetro;
            Peca.RodobancaP1Esquerda = RodobancaP1Esquerda; Peca.RodobancaP1Direita = RodobancaP1Direita;
            Peca.RodobancaP1Frente = RodobancaP1Frente; Peca.RodobancaP1Tras = RodobancaP1Tras;
            Peca.RodobancaP2Esquerda = RodobancaP2Esquerda; Peca.RodobancaP2Direita = RodobancaP2Direita;
            Peca.RodobancaP2Frente = RodobancaP2Frente; Peca.RodobancaP2Tras = RodobancaP2Tras;
            Peca.RodobancaP3Esquerda = RodobancaP3Esquerda; Peca.RodobancaP3Direita = RodobancaP3Direita;
            Peca.RodobancaP3Frente = RodobancaP3Frente; Peca.RodobancaP3Tras = RodobancaP3Tras;

            Peca.SaiaP1Esquerda = SaiaP1Esquerda; Peca.SaiaP1Direita = SaiaP1Direita;
            Peca.SaiaP1Frente = SaiaP1Frente; Peca.SaiaP1Tras = SaiaP1Tras;
            Peca.SaiaP2Esquerda = SaiaP2Esquerda; Peca.SaiaP2Direita = SaiaP2Direita;
            Peca.SaiaP2Frente = SaiaP2Frente; Peca.SaiaP2Tras = SaiaP2Tras;
            Peca.SaiaP3Esquerda = SaiaP3Esquerda; Peca.SaiaP3Direita = SaiaP3Direita;
            Peca.SaiaP3Frente = SaiaP3Frente; Peca.SaiaP3Tras = SaiaP3Tras;

            // BOJO
            Peca.LarguraBojo = ConverterParaDouble(LarguraBojoInput);
            Peca.AlturaBojo = ConverterParaDouble(AlturaBojoInput);

            Peca.BojoX = ConverterParaDouble(BojoXInput);
            Peca.BojoY = ConverterParaDouble(BojoYInput);

            Peca.TemBojo = TemBojo;
            Peca.PecaDestinoBojo = PecaDestinoBojo;

            // COOKTOP
            Peca.LarguraCooktop = ConverterParaDouble(LarguraCooktopInput);
            Peca.AlturaCooktop = ConverterParaDouble(AlturaCooktopInput);

            Peca.CooktopX = ConverterParaDouble(CooktopXInput);
            Peca.CooktopY = ConverterParaDouble(CooktopYInput);

            Peca.TemCooktop = TemCooktop;
            Peca.PecaDestinoCooktop = PecaDestinoCooktop;

            Peca.Quantidade = Quantidade; Peca.ValorTotalPeca = TotalGeral; Peca.ValorMetroLinear = ConverterParaDouble(ValorMetroLinearInput);
            await Shell.Current.GoToAsync("..", new Dictionary<string, object> { { "NovaPeca", Peca } });
        }

        private async Task CarregarEstoque() { 
            try {
                var itens = await _dbService.GetItemsAsync<EstoqueItem>();
                MainThread.BeginInvokeOnMainThread(() => { ListaEstoque.Clear(); foreach (var item in itens) ListaEstoque.Add(item); });
            } catch { }
        }
    }
}