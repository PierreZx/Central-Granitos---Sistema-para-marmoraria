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

        public bool PodeEditarP2Direita => LadoP2 != "Esquerda";
        public bool PodeEditarP2Esquerda => LadoP2 != "Direita";
        public bool PodeEditarP3Esquerda => LadoP3 != "Direita";
        public bool PodeEditarP3Direita => LadoP3 != "Esquerda";

        public IDrawable DesenhoPeca { get; }

        public CalculadoraPecaViewModel(DatabaseService dbService)
        {
            _dbService = dbService;
            DesenhoPeca = new PecaDrawable(this);
            _ = CarregarEstoque();
            
            Peca2.Largura = 0; Peca2.Altura = 0;
            Peca3.Largura = 0; Peca3.Altura = 0;
        }

        // ==========================================
        // COMANDOS E SINCRONIZAÇÃO
        // ==========================================

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
            TotalGeral = ((areaTotal * PedraSelecionada.ValorPorMetro) + (linearTotal * valorML)) * Quantidade;
        }

        // ==========================================
        // NAVEGAÇÃO DE ABAS
        // ==========================================
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

        // INTERCEPTADORES
        partial void OnRodobancaP1EsquerdaChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP1DireitaChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP1FrenteChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP1TrasChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP2EsquerdaChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP2DireitaChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP2FrenteChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP2TrasChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP3EsquerdaChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP3DireitaChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP3FrenteChanged(double value) => NotificarMudanca();
        partial void OnRodobancaP3TrasChanged(double value) => NotificarMudanca();
        partial void OnSaiaP1EsquerdaChanged(double value) => NotificarMudanca();
        partial void OnSaiaP1DireitaChanged(double value) => NotificarMudanca();
        partial void OnSaiaP1FrenteChanged(double value) => NotificarMudanca();
        partial void OnSaiaP1TrasChanged(double value) => NotificarMudanca();
        partial void OnSaiaP2EsquerdaChanged(double value) => NotificarMudanca();
        partial void OnSaiaP2DireitaChanged(double value) => NotificarMudanca();
        partial void OnSaiaP2FrenteChanged(double value) => NotificarMudanca();
        partial void OnSaiaP2TrasChanged(double value) => NotificarMudanca();
        partial void OnSaiaP3EsquerdaChanged(double value) => NotificarMudanca();
        partial void OnSaiaP3DireitaChanged(double value) => NotificarMudanca();
        partial void OnSaiaP3FrenteChanged(double value) => NotificarMudanca();
        partial void OnSaiaP3TrasChanged(double value) => NotificarMudanca();
        partial void OnTemBojoChanged(bool value) => NotificarMudanca();
        partial void OnPecaDestinoBojoChanged(string value) => NotificarMudanca();
        partial void OnTemCooktopChanged(bool value) => NotificarMudanca();
        partial void OnPecaDestinoCooktopChanged(string value) => NotificarMudanca();

        // ==========================================
        // LÓGICA DE SALVAMENTO E EDIÇÃO (PERSISTÊNCIA)
        // ==========================================
        public void ApplyQueryAttributes(IDictionary<string, object> query)
        {
            if (query.TryGetValue("PecaParaEditar", out var pecaObj) && pecaObj is PecaOrcamento edicao)
            {
                Peca = edicao;
                
                // Mapear medidas P1
                LarguraInput = edicao.Largura.ToString("N2");
                AlturaInput = edicao.Altura.ToString("N2");

                // Mapear pernas P2 e P3
                LarguraP2Input = edicao.LarguraP2.ToString("N2");
                AlturaP2Input = edicao.AlturaP2.ToString("N2");
                LadoP2 = edicao.LadoP2;
                LarguraP3Input = edicao.LarguraP3.ToString("N2");
                AlturaP3Input = edicao.AlturaP3.ToString("N2");

                // Mapear Acabamentos Rodobanca
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

                // Mapear Acabamentos Saia
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

                // Mapear Recortes
                TemBojo = edicao.TemBojo;
                PecaDestinoBojo = edicao.PecaDestinoBojo;
                LarguraBojoInput = edicao.LarguraBojo.ToString("N2");
                AlturaBojoInput = edicao.AlturaBojo.ToString("N2");
                BojoXInput = edicao.BojoX.ToString("N2");

                TemCooktop = edicao.TemCooktop;
                PecaDestinoCooktop = edicao.PecaDestinoCooktop;
                LarguraCooktopInput = edicao.LarguraCooktop.ToString("N2");
                AlturaCooktopInput = edicao.AlturaCooktop.ToString("N2");
                CooktopXInput = edicao.CooktopX.ToString("N2");

                NotificarMudanca(); // Força o desenho a aparecer após carregar tudo
            }
        }

        [RelayCommand]
        private async Task SalvarPeca()
        {
            if (PedraSelecionada == null)
            {
                await Shell.Current.DisplayAlert("Aviso", "Selecione o material!", "OK");
                return;
            }

            // Atualizar o objeto Peca com os dados finais dos Inputs para salvar no banco
            Peca.Largura = ConverterParaDouble(LarguraInput);
            Peca.Altura = ConverterParaDouble(AlturaInput);
            Peca.LarguraP2 = ConverterParaDouble(LarguraP2Input);
            Peca.AlturaP2 = ConverterParaDouble(AlturaP2Input);
            Peca.LadoP2 = LadoP2;
            Peca.LarguraP3 = ConverterParaDouble(LarguraP3Input);
            Peca.AlturaP3 = ConverterParaDouble(AlturaP3Input);
            Peca.LadoP3 = LadoP3;

            // Sincronizar Acabamentos Rodobanca no objeto
            Peca.RodobancaP1Esquerda = RodobancaP1Esquerda;
            Peca.RodobancaP1Direita = RodobancaP1Direita;
            Peca.RodobancaP1Frente = RodobancaP1Frente;
            Peca.RodobancaP1Tras = RodobancaP1Tras;
            Peca.RodobancaP2Esquerda = RodobancaP2Esquerda;
            Peca.RodobancaP2Direita = RodobancaP2Direita;
            Peca.RodobancaP2Frente = RodobancaP2Frente;
            Peca.RodobancaP2Tras = RodobancaP2Tras;
            Peca.RodobancaP3Esquerda = RodobancaP3Esquerda;
            Peca.RodobancaP3Direita = RodobancaP3Direita;
            Peca.RodobancaP3Frente = RodobancaP3Frente;
            Peca.RodobancaP3Tras = RodobancaP3Tras;

            // Sincronizar Acabamentos Saia no objeto
            Peca.SaiaP1Esquerda = SaiaP1Esquerda;
            Peca.SaiaP1Direita = SaiaP1Direita;
            Peca.SaiaP1Frente = SaiaP1Frente;
            Peca.SaiaP1Tras = SaiaP1Tras;
            Peca.SaiaP2Esquerda = SaiaP2Esquerda;
            Peca.SaiaP2Direita = SaiaP2Direita;
            Peca.SaiaP2Frente = SaiaP2Frente;
            Peca.SaiaP2Tras = SaiaP2Tras;
            Peca.SaiaP3Esquerda = SaiaP3Esquerda;
            Peca.SaiaP3Direita = SaiaP3Direita;
            Peca.SaiaP3Frente = SaiaP3Frente;
            Peca.SaiaP3Tras = SaiaP3Tras;

            // Sincronizar Recortes no objeto
            Peca.TemBojo = TemBojo;
            Peca.PecaDestinoBojo = PecaDestinoBojo;
            Peca.LarguraBojo = ConverterParaDouble(LarguraBojoInput);
            Peca.AlturaBojo = ConverterParaDouble(AlturaBojoInput);
            Peca.BojoX = ConverterParaDouble(BojoXInput);

            Peca.TemCooktop = TemCooktop;
            Peca.PecaDestinoCooktop = PecaDestinoCooktop;
            Peca.LarguraCooktop = ConverterParaDouble(LarguraCooktopInput);
            Peca.AlturaCooktop = ConverterParaDouble(AlturaCooktopInput);
            Peca.CooktopX = ConverterParaDouble(CooktopXInput);

            // Dados Finais
            Peca.PedraNome = PedraSelecionada.NomeChapa;
            Peca.ValorM2 = PedraSelecionada.ValorPorMetro;
            Peca.ValorMetroLinear = ConverterParaDouble(ValorMetroLinearInput);
            Peca.Quantidade = Quantidade;
            Peca.UsarMultiplicador = UsarMultiplicador;
            Peca.ValorTotalPeca = TotalGeral; // Importante para o binding no DetalheClientePage

            await Shell.Current.GoToAsync("..", new Dictionary<string, object> { { "NovaPeca", Peca } });
        }

        private async Task CarregarEstoque() { 
            var itens = await _dbService.GetItemsAsync<EstoqueItem>();
            MainThread.BeginInvokeOnMainThread(() => {
                ListaEstoque.Clear();
                foreach (var item in itens) ListaEstoque.Add(item);
            });
        }
    }
}