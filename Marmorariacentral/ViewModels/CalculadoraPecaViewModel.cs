using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using Marmorariacentral.Drawables;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Globalization;
using Microsoft.Maui.Graphics;

namespace Marmorariacentral.ViewModels
{
    public partial class CalculadoraPecaViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;
        // ADICIONE ESTA FLAG
        private bool _isLoading = false;

        // ==========================================
        // OBJETOS DE DADOS E ESTADO
        // ==========================================
        [ObservableProperty] private PecaOrcamento peca = new();
        [ObservableProperty] private PecaOrcamento peca2 = new();
        [ObservableProperty] private PecaOrcamento peca3 = new();

        [ObservableProperty] private ObservableCollection<EstoqueItem> listaEstoque = new();
        [ObservableProperty] private EstoqueItem? pedraSelecionada;
        [ObservableProperty] private double valorMaoDeObra;
        [ObservableProperty] private double totalGeral;
        
        [ObservableProperty] private string ladoP2 = "Esquerda";
        [ObservableProperty] private string ladoP3 = "Direita";
        public List<string> LadosDisponiveis { get; } = new() { "Esquerda", "Direita" };
        public List<string> PecasDisponiveis { get; } = new() { "P1", "P2", "P3" };

        // INPUTS DE TEXTO (CORREÇÃO VÍRGULA/APAGAR)
        [ObservableProperty] private string larguraInput = "0,00";
        [ObservableProperty] private string alturaInput = "0,00";
        [ObservableProperty] private string larguraP2Input = "0,00";
        [ObservableProperty] private string alturaP2Input = "0,00";
        [ObservableProperty] private string larguraP3Input = "0,00";
        [ObservableProperty] private string alturaP3Input = "0,00";
        [ObservableProperty] private string valorMetroLinearInput = "130";
        [ObservableProperty] private string quantidadeInput = "1";
        [ObservableProperty] private bool usarMultiplicador = false;

        public int Quantidade => int.TryParse(QuantidadeInput, out int q) ? Math.Max(q, 1) : 1;
        public double ValorMaterial => Peca?.ValorTotalPeca ?? 0;

        // ==========================================
        // RECORTES (BOJO E COOKTOP)
        // ==========================================
        [ObservableProperty] private bool temBojo = false;
        [ObservableProperty] private string pecaDestinoBojo = "P1";
        [ObservableProperty] private string larguraBojoInput = "0,60";
        [ObservableProperty] private string alturaBojoInput = "0,40";
        [ObservableProperty] private string bojoXInput = "0,50";

        [ObservableProperty] private bool temCooktop = false;
        [ObservableProperty] private string pecaDestinoCooktop = "P1";
        [ObservableProperty] private string larguraCooktopInput = "0,55";
        [ObservableProperty] private string alturaCooktopInput = "0,45";
        [ObservableProperty] private string cooktopXInput = "1,50";

        // ==========================================
        // RODOBANCA - TODAS AS PROPRIEDADES (P1, P2, P3)
        // ==========================================
        [ObservableProperty] private double rodobancaP1Esquerda = 0.10;
        [ObservableProperty] private double rodobancaP1Direita = 0.10;
        [ObservableProperty] private double rodobancaP1Frente = 0.00;
        [ObservableProperty] private double rodobancaP1Tras = 0.10;
        [ObservableProperty] private double rodobancaP2Esquerda = 0.10;
        [ObservableProperty] private double rodobancaP2Direita = 0.10;
        [ObservableProperty] private double rodobancaP2Frente = 0.00;
        [ObservableProperty] private double rodobancaP2Tras = 0.10;
        [ObservableProperty] private double rodobancaP3Esquerda = 0.10;
        [ObservableProperty] private double rodobancaP3Direita = 0.10;
        [ObservableProperty] private double rodobancaP3Frente = 0.00;
        [ObservableProperty] private double rodobancaP3Tras = 0.10;

        // ==========================================
        // SAIA - TODAS AS PROPRIEDADES (P1, P2, P3)
        // ==========================================
        [ObservableProperty] private double saiaP1Esquerda = 0.00;
        [ObservableProperty] private double saiaP1Direita = 0.00;
        [ObservableProperty] private double saiaP1Frente = 0.04;
        [ObservableProperty] private double saiaP1Tras = 0.00;
        [ObservableProperty] private double saiaP2Esquerda = 0.00;
        [ObservableProperty] private double saiaP2Direita = 0.00;
        [ObservableProperty] private double saiaP2Frente = 0.04;
        [ObservableProperty] private double saiaP2Tras = 0.00;
        [ObservableProperty] private double saiaP3Esquerda = 0.00;
        [ObservableProperty] private double saiaP3Direita = 0.00;
        [ObservableProperty] private double saiaP3Frente = 0.04;
        [ObservableProperty] private double saiaP3Tras = 0.00;

        // ==========================================
        // LÓGICA DE VISIBILIDADE E TRAVAS
        // ==========================================
        public bool TemPernaEsquerda => ConverterParaDouble(LarguraP2Input) > 0.01 && LadoP2 == "Esquerda";
        public bool TemPernaDireita => (ConverterParaDouble(LarguraP2Input) > 0.01 && LadoP2 == "Direita") || (ConverterParaDouble(LarguraP3Input) > 0.01);
        public bool PodeEditarP1Esquerda => !TemPernaEsquerda;
        public bool PodeEditarP1Direita => !TemPernaDireita;

        public IDrawable DesenhoPeca { get; }

        public CalculadoraPecaViewModel(DatabaseService dbService)
        {
            _dbService = dbService;
            DesenhoPeca = new PecaDrawable(this);
            _ = CarregarEstoque();
            Peca2.Largura = 0; Peca2.Altura = 0;
            Peca3.Largura = 0; Peca3.Altura = 0;
        }

        [RelayCommand]
        public void NotificarMudanca()
        {
            ProcessarTodasAsMedidas();
            MainThread.BeginInvokeOnMainThread(() =>
            {
                OnPropertyChanged(nameof(DesenhoPeca));
                OnPropertyChanged(nameof(TemPernaEsquerda));
                OnPropertyChanged(nameof(TemPernaDireita));
                OnPropertyChanged(nameof(ValorMaterial));
                OnPropertyChanged(nameof(TotalGeral));
            });
        }

        private void ProcessarTodasAsMedidas()
        {
            // Forçamos a atualização dos valores numéricos baseados nas strings dos Entry
            Peca.Largura = ConverterParaDouble(LarguraInput);
            Peca.Altura = ConverterParaDouble(AlturaInput); 
            
            Peca2.Largura = ConverterParaDouble(LarguraP2Input);
            Peca2.Altura = ConverterParaDouble(AlturaP2Input);
            
            Peca3.Largura = ConverterParaDouble(LarguraP3Input);
            Peca3.Altura = ConverterParaDouble(AlturaP3Input);
            
            CalcularTotal();
        }

        private double ConverterParaDouble(string valor)
        {
            if (string.IsNullOrWhiteSpace(valor)) return 0;
            string limpo = valor.Replace(',', '.');
            return double.TryParse(limpo, CultureInfo.InvariantCulture, out double result) ? result : 0;
        }

        private void CalcularTotal()
        {
            if (PedraSelecionada == null) return;
            double areaTotal = (Peca.Largura * Peca.Altura) + (Peca2.Largura * Peca2.Altura) + (Peca3.Largura * Peca3.Altura);
            double valorML = ConverterParaDouble(ValorMetroLinearInput);
            double linearTotal = Peca.Largura + Peca2.Largura + Peca3.Largura;
            int qf = UsarMultiplicador ? Quantidade : 1;
            TotalGeral = ((areaTotal * PedraSelecionada.ValorPorMetro) + (linearTotal * valorML)) * qf;
        }

        [ObservableProperty] private string abaAtiva = "Principal";
        partial void OnAbaAtivaChanged(string value)
        {
            OnPropertyChanged(nameof(IsAbaPrincipalVisible));
            OnPropertyChanged(nameof(IsAbaRodobancaVisible));
            OnPropertyChanged(nameof(IsAbaSaiaVisible));
            OnPropertyChanged(nameof(IsAbaRecortesVisible));
        }

        public bool IsAbaPrincipalVisible => AbaAtiva == "Principal";
        public bool IsAbaRodobancaVisible => AbaAtiva == "Rodobanca";
        public bool IsAbaSaiaVisible => AbaAtiva == "Saia";
        public bool IsAbaRecortesVisible => AbaAtiva == "Recortes";

        [RelayCommand] private void MostrarAbaPrincipal() => AbaAtiva = "Principal";
        [RelayCommand] private void MostrarAbaRodobanca() => AbaAtiva = "Rodobanca";
        [RelayCommand] private void MostrarAbaSaia() => AbaAtiva = "Saia";
        [RelayCommand] private void MostrarAbaRecortes() => AbaAtiva = "Recortes";

        // MODIFIQUE TODOS OS PARTIAL METHODS PARA VERIFICAR A FLAG
        partial void OnRodobancaP1EsquerdaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP1DireitaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP1FrenteChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP1TrasChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP2EsquerdaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP2DireitaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP2FrenteChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP2TrasChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP3EsquerdaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP3DireitaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP3FrenteChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnRodobancaP3TrasChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP1EsquerdaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP1DireitaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP1FrenteChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP1TrasChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP2EsquerdaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP2DireitaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP2FrenteChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP2TrasChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP3EsquerdaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP3DireitaChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP3FrenteChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnSaiaP3TrasChanged(double value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnTemBojoChanged(bool value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnPecaDestinoBojoChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnTemCooktopChanged(bool value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnPecaDestinoCooktopChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnPedraSelecionadaChanged(EstoqueItem? value) { if (!_isLoading) NotificarMudanca(); }
        
        // MODIFIQUE OS INPUTS TAMBÉM
        partial void OnLarguraInputChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnAlturaInputChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnLarguraP2InputChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnAlturaP2InputChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnLarguraP3InputChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnAlturaP3InputChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnValorMetroLinearInputChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnUsarMultiplicadorChanged(bool value) { if (!_isLoading) NotificarMudanca(); }
        partial void OnQuantidadeInputChanged(string value) { if (!_isLoading) NotificarMudanca(); }
        
        partial void OnLadoP2Changed(string value) 
        { 
            LadoP3 = value == "Esquerda" ? "Direita" : "Esquerda"; 
            if (!_isLoading) NotificarMudanca(); 
        }

        public void ApplyQueryAttributes(IDictionary<string, object> query)
            {
                if (!query.TryGetValue("PecaParaEditar", out var pecaObj) || pecaObj is not PecaOrcamento edicao)
                    return;

                _isLoading = true;

                try
                {
                    // =============================
                    // 1️⃣ DADOS BÁSICOS
                    // =============================
                    Peca.Id = edicao.Id;
                    Peca.ClienteId = edicao.ClienteId;
                    Peca.Ambiente = edicao.Ambiente;
                    Peca.PedraNome = edicao.PedraNome;
                    Peca.ValorM2 = edicao.ValorM2;
                    Peca.ValorMetroLinear = edicao.ValorMetroLinear;
                    Peca.Quantidade = edicao.Quantidade;
                    Peca.UsarMultiplicador = edicao.UsarMultiplicador;
                    Peca.ValorTotalPeca = edicao.ValorTotalPeca;

                    // =============================
                    // 2️⃣ MEDIDAS P1
                    // =============================
                    Peca.Largura = edicao.Largura;
                    Peca.Altura = edicao.Altura;

                    LarguraInput = edicao.Largura.ToString("N2", CultureInfo.CurrentCulture);
                    AlturaInput = edicao.Altura.ToString("N2", CultureInfo.CurrentCulture);

                    // =============================
                    // 3️⃣ MEDIDAS P2
                    // =============================
                    Peca.LarguraP2 = edicao.LarguraP2;
                    Peca.AlturaP2 = edicao.AlturaP2;
                    Peca.LadoP2 = edicao.LadoP2;

                    LadoP2 = edicao.LadoP2;
                    LarguraP2Input = edicao.LarguraP2.ToString("N2", CultureInfo.CurrentCulture);
                    AlturaP2Input = edicao.AlturaP2.ToString("N2", CultureInfo.CurrentCulture);

                    // =============================
                    // 4️⃣ MEDIDAS P3
                    // =============================
                    Peca.LarguraP3 = edicao.LarguraP3;
                    Peca.AlturaP3 = edicao.AlturaP3;
                    Peca.LadoP3 = edicao.LadoP3;

                    LarguraP3Input = edicao.LarguraP3.ToString("N2", CultureInfo.CurrentCulture);
                    AlturaP3Input = edicao.AlturaP3.ToString("N2", CultureInfo.CurrentCulture);

                    // =============================
                    // 5️⃣ RODOBANCAS
                    // =============================
                    RodobancaP1Esquerda = edicao.RodobancaP1Esquerda;
                    RodobancaP1Direita = edicao.RodobancaP1Direita;
                    RodobancaP1Frente = edicao.RodobancaP1Frente;
                    RodobancaP1Tras = edicao.RodobancaP1Tras;

                    RodobancaP2Esquerda = edicao.RodobancaP2Esquerda;
                    RodobancaP2Direita = edicao.RodobancaP2Direita;
                    RodobancaP2Frente = edicao.RodobancaP2Frente;
                    RodobancaP2Tras = edicao.RodobancaP2Tras;

                    RodobancaP3Esquerda = edicao.RodobancaP3Esquerda;
                    RodobancaP3Direita = edicao.RodobancaP3Direita;
                    RodobancaP3Frente = edicao.RodobancaP3Frente;
                    RodobancaP3Tras = edicao.RodobancaP3Tras;

                    // =============================
                    // 6️⃣ SAIAS
                    // =============================
                    SaiaP1Esquerda = edicao.SaiaP1Esquerda;
                    SaiaP1Direita = edicao.SaiaP1Direita;
                    SaiaP1Frente = edicao.SaiaP1Frente;
                    SaiaP1Tras = edicao.SaiaP1Tras;

                    SaiaP2Esquerda = edicao.SaiaP2Esquerda;
                    SaiaP2Direita = edicao.SaiaP2Direita;
                    SaiaP2Frente = edicao.SaiaP2Frente;
                    SaiaP2Tras = edicao.SaiaP2Tras;

                    SaiaP3Esquerda = edicao.SaiaP3Esquerda;
                    SaiaP3Direita = edicao.SaiaP3Direita;
                    SaiaP3Frente = edicao.SaiaP3Frente;
                    SaiaP3Tras = edicao.SaiaP3Tras;

                    // =============================
                    // 7️⃣ RECORTES
                    // =============================
                    TemBojo = edicao.TemBojo;
                    PecaDestinoBojo = edicao.PecaDestinoBojo;
                    LarguraBojoInput = edicao.LarguraBojo.ToString("N2", CultureInfo.CurrentCulture);
                    AlturaBojoInput = edicao.AlturaBojo.ToString("N2", CultureInfo.CurrentCulture);
                    BojoXInput = edicao.BojoX.ToString("N2", CultureInfo.CurrentCulture);

                    TemCooktop = edicao.TemCooktop;
                    PecaDestinoCooktop = edicao.PecaDestinoCooktop;
                    LarguraCooktopInput = edicao.LarguraCooktop.ToString("N2", CultureInfo.CurrentCulture);
                    AlturaCooktopInput = edicao.AlturaCooktop.ToString("N2", CultureInfo.CurrentCulture);
                    CooktopXInput = edicao.CooktopX.ToString("N2", CultureInfo.CurrentCulture);

                    // =============================
                    // 8️⃣ MATERIAL
                    // =============================
                    ValorMetroLinearInput = edicao.ValorMetroLinear.ToString("N2", CultureInfo.CurrentCulture);
                    QuantidadeInput = edicao.Quantidade.ToString();
                    UsarMultiplicador = edicao.UsarMultiplicador;

                    if (ListaEstoque != null && ListaEstoque.Any())
                    {
                        PedraSelecionada = ListaEstoque.FirstOrDefault(p => p.NomeChapa == edicao.PedraNome);
                    }
                }
                finally
                {
                    _isLoading = false;

                    // 🔥 FORÇA SINCRONIZAÇÃO COMPLETA
                    ProcessarTodasAsMedidas();
                    NotificarMudanca();
                }
            }


        [RelayCommand]
        private async Task SalvarPeca()
        {
            if (PedraSelecionada == null) { await Shell.Current.DisplayAlert("Aviso", "Selecione o material!", "OK"); return; }

            // Sincroniza os valores finais das inputs antes de fechar
            Peca.Largura = ConverterParaDouble(LarguraInput);
            Peca.Altura = ConverterParaDouble(AlturaInput); 
            Peca.LarguraP2 = ConverterParaDouble(LarguraP2Input);
            Peca.AlturaP2 = ConverterParaDouble(AlturaP2Input);
            Peca.LadoP2 = LadoP2;
            Peca.LarguraP3 = ConverterParaDouble(LarguraP3Input);
            Peca.AlturaP3 = ConverterParaDouble(AlturaP3Input);
            Peca.LadoP3 = LadoP2 == "Esquerda" ? "Direita" : "Esquerda";

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

            Peca.TemBojo = TemBojo; Peca.PecaDestinoBojo = PecaDestinoBojo;
            Peca.LarguraBojo = ConverterParaDouble(LarguraBojoInput);
            Peca.AlturaBojo = ConverterParaDouble(AlturaBojoInput);
            Peca.BojoX = ConverterParaDouble(BojoXInput);

            Peca.TemCooktop = TemCooktop; Peca.PecaDestinoCooktop = PecaDestinoCooktop;
            Peca.LarguraCooktop = ConverterParaDouble(LarguraCooktopInput);
            Peca.AlturaCooktop = ConverterParaDouble(AlturaCooktopInput);
            Peca.CooktopX = ConverterParaDouble(CooktopXInput);

            Peca.PedraNome = PedraSelecionada.NomeChapa;
            Peca.ValorM2 = PedraSelecionada.ValorPorMetro;
            Peca.ValorMetroLinear = ConverterParaDouble(ValorMetroLinearInput);
            Peca.Quantidade = Quantidade;
            Peca.UsarMultiplicador = UsarMultiplicador;
            Peca.ValorTotalPeca = TotalGeral;

            await Shell.Current.GoToAsync("..", new Dictionary<string, object> { { "NovaPeca", Peca } });
        }

        private async Task CarregarEstoque() { 
            var itens = await _dbService.GetItemsAsync<EstoqueItem>();
            MainThread.BeginInvokeOnMainThread(() => {
                ListaEstoque.Clear();
                foreach (var item in itens) ListaEstoque.Add(item);
                if (Peca != null && !string.IsNullOrEmpty(Peca.PedraNome))
                {
                    PedraSelecionada = ListaEstoque.FirstOrDefault(p => p.NomeChapa == Peca.PedraNome);
                }
            });
        }
    }
}