using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Globalization;
using Microsoft.Maui.Graphics;
using Microsoft.Maui.ApplicationModel;

namespace Marmorariacentral.ViewModels
{
    public partial class CalculadoraPecaViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;

        // =========================
        // PEÇA PRINCIPAL (P1)
        // =========================

        [ObservableProperty]
        private PecaOrcamento peca = new();

        [ObservableProperty]
        private string larguraInput = "0,00";

        [ObservableProperty]
        private string alturaInput = "0,00";

        [ObservableProperty]
        private string valorMetroLinearInput = "130";

        [ObservableProperty]
        private bool usarMultiplicador = false;

        [ObservableProperty]
        private string quantidadeInput = "1";

        public int Quantidade =>
            int.TryParse(QuantidadeInput, out int q) ? Math.Max(q, 1) : 1;

        public double ValorMaterial => Peca?.ValorTotalPeca ?? 0;

        // =========================
        // BANCADA EM L (P2)
        // =========================

        [ObservableProperty]
        private PecaOrcamento peca2 = new();

        [ObservableProperty]
        private string ladoP2 = "Esquerda";

        // =========================
        // BANCADA EM U (P3)
        // =========================

        [ObservableProperty]
        private PecaOrcamento peca3 = new();

        [ObservableProperty]
        private string ladoP3 = "Direita";

        public List<string> LadosDisponiveis { get; } =
            new() { "Esquerda", "Direita" };

        // =========================
        // RODOBANCA - TODOS OS LADOS DE TODAS AS PEÇAS
        // =========================

        // P1 - Peça Principal
        [ObservableProperty]
        private double rodobancaP1Esquerda = 0.10;
        [ObservableProperty]
        private double rodobancaP1Direita = 0.10;
        [ObservableProperty]
        private double rodobancaP1Frente = 0.10;    // Inferior
        [ObservableProperty]
        private double rodobancaP1Tras = 0.10;      // Superior

        // P2 - Bancada em L
        [ObservableProperty]
        private double rodobancaP2Esquerda = 0.10;
        [ObservableProperty]
        private double rodobancaP2Direita = 0.10;
        [ObservableProperty]
        private double rodobancaP2Frente = 0.10;
        [ObservableProperty]
        private double rodobancaP2Tras = 0.10;

        // P3 - Bancada em U
        [ObservableProperty]
        private double rodobancaP3Esquerda = 0.10;
        [ObservableProperty]
        private double rodobancaP3Direita = 0.10;
        [ObservableProperty]
        private double rodobancaP3Frente = 0.10;
        [ObservableProperty]
        private double rodobancaP3Tras = 0.10;

        // =========================
        // SAIA - TODOS OS LADOS DE TODAS AS PEÇAS
        // =========================

        // P1 - Peça Principal
        [ObservableProperty]
        private double saiaP1Esquerda = 0.10;
        [ObservableProperty]
        private double saiaP1Direita = 0.10;
        [ObservableProperty]
        private double saiaP1Frente = 0.10;
        [ObservableProperty]
        private double saiaP1Tras = 0.10;

        // P2 - Bancada em L
        [ObservableProperty]
        private double saiaP2Esquerda = 0.10;
        [ObservableProperty]
        private double saiaP2Direita = 0.10;
        [ObservableProperty]
        private double saiaP2Frente = 0.10;
        [ObservableProperty]
        private double saiaP2Tras = 0.10;

        // P3 - Bancada em U
        [ObservableProperty]
        private double saiaP3Esquerda = 0.10;
        [ObservableProperty]
        private double saiaP3Direita = 0.10;
        [ObservableProperty]
        private double saiaP3Frente = 0.10;
        [ObservableProperty]
        private double saiaP3Tras = 0.10;

        // =========================
        // CONTROLE DE LADOS COLADOS (desabilitados)
        // =========================

        public bool IsP1EsquerdaColada => TemPernaEsquerda;
        public bool IsP1DireitaColada => TemPernaDireita;
        public bool IsP2DireitaColada => TemPernaDireita && LadoP2 == "Esquerda";
        public bool IsP2EsquerdaColada => TemPernaEsquerda && LadoP2 == "Direita";
        public bool IsP3DireitaColada => TemPernaDireita && LadoP3 == "Esquerda";
        public bool IsP3EsquerdaColada => TemPernaEsquerda && LadoP3 == "Direita";
        
        // Lados que sempre estão livres (frente/tras)
        public bool IsP1FrenteColada => false;
        public bool IsP1TrasColada => false;
        public bool IsP2FrenteColada => false;
        public bool IsP2TrasColada => false;
        public bool IsP3FrenteColada => false;
        public bool IsP3TrasColada => false;

        // =========================
        // CONTROLE DE VISIBILIDADE DAS PEÇAS
        // =========================

        public bool TemPernaEsquerda => Peca2.Largura > 0 && Peca2.Altura > 0 && LadoP2 == "Esquerda";
        public bool TemPernaDireita => (Peca2.Largura > 0 && Peca2.Altura > 0 && LadoP2 == "Direita") ||
                                      (Peca3.Largura > 0 && Peca3.Altura > 0);

        // =========================
        // CONTROLE DE ABAS
        // =========================
        private string _abaAtiva = "Principal";
        public string AbaAtiva
        {
            get => _abaAtiva;
            set
            {
                if (SetProperty(ref _abaAtiva, value))
                {
                    OnPropertyChanged(nameof(IsAbaPrincipalVisible));
                    OnPropertyChanged(nameof(IsAbaRodobancaVisible));
                    OnPropertyChanged(nameof(IsAbaSaiaVisible));
                }
            }
        }

        public bool IsAbaPrincipalVisible => AbaAtiva == "Principal";
        public bool IsAbaRodobancaVisible => AbaAtiva == "Rodobanca";
        public bool IsAbaSaiaVisible => AbaAtiva == "Saia";

        // =========================
        // ESTOQUE E TOTAIS
        // =========================

        [ObservableProperty]
        private ObservableCollection<EstoqueItem> listaEstoque = new();

        [ObservableProperty]
        private EstoqueItem? pedraSelecionada;

        [ObservableProperty]
        private double valorMaoDeObra;

        [ObservableProperty]
        private double totalGeral;

        public IDrawable DesenhoPeca { get; }

        public CalculadoraPecaViewModel(DatabaseService dbService)
        {
            _dbService = dbService;
            DesenhoPeca = new PecaDrawable(this);
            _ = CarregarEstoque();
            
            // Inicializa com valores padrão
            Peca2.Largura = 0;
            Peca2.Altura = 0;
            Peca3.Largura = 0;
            Peca3.Altura = 0;
        }

        // =========================
        // QUERY
        // =========================

        public void ApplyQueryAttributes(IDictionary<string, object> query)
        {
            if (query.TryGetValue("PecaParaEditar", out var pecaObj) && pecaObj is PecaOrcamento pecaEdicao)
            {
                Peca = pecaEdicao;
                LarguraInput = pecaEdicao.Largura.ToString("N2", CultureInfo.CurrentCulture);
                AlturaInput = pecaEdicao.Altura.ToString("N2", CultureInfo.CurrentCulture);
            }
        }

        // =========================
        // ESTOQUE
        // =========================

        private async Task CarregarEstoque()
        {
            try
            {
                var itens = await _dbService.GetItemsAsync<EstoqueItem>();
                MainThread.BeginInvokeOnMainThread(() =>
                {
                    ListaEstoque.Clear();
                    foreach (var item in itens)
                        ListaEstoque.Add(item);
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine(ex.Message);
            }
        }

        // =========================
        // COMANDOS PARA NAVEGAÇÃO DE ABAS
        // =========================
        [RelayCommand]
        private void MostrarAbaPrincipal() => AbaAtiva = "Principal";
        
        [RelayCommand]
        private void MostrarAbaRodobanca() => AbaAtiva = "Rodobanca";
        
        [RelayCommand]
        private void MostrarAbaSaia() => AbaAtiva = "Saia";

        // =========================
        // EVENTOS - ATUALIZAÇÃO INSTANTÂNEA
        // =========================

        partial void OnPedraSelecionadaChanged(EstoqueItem? value) => CalcularTotal();
        partial void OnLarguraInputChanged(string value) => ProcessarMudancaMedida();
        partial void OnAlturaInputChanged(string value) => ProcessarMudancaMedida();
        partial void OnValorMetroLinearInputChanged(string value) => CalcularTotal();
        partial void OnQuantidadeInputChanged(string value) => CalcularTotal();
        partial void OnUsarMultiplicadorChanged(bool value) => CalcularTotal();
        
        partial void OnLadoP2Changed(string value) 
        { 
            AtualizarLadoP3(); 
            ForcarAtualizacaoCompleta();
        }
        
        partial void OnLadoP3Changed(string value) 
        { 
            ForcarAtualizacaoCompleta();
        }

        partial void OnPeca2Changed(PecaOrcamento value)
        {
            ForcarAtualizacaoCompleta();
        }

        partial void OnPeca3Changed(PecaOrcamento value)
        {
            ForcarAtualizacaoCompleta();
        }

        private void AtualizarLadoP3()
        {
            LadoP3 = LadoP2 == "Esquerda" ? "Direita" : "Esquerda";
        }

        private void ForcarAtualizacaoCompleta()
        {
            MainThread.BeginInvokeOnMainThread(() =>
            {
                OnPropertyChanged(nameof(DesenhoPeca));
                OnPropertyChanged(nameof(TemPernaEsquerda));
                OnPropertyChanged(nameof(TemPernaDireita));
                OnPropertyChanged(nameof(IsP1EsquerdaColada));
                OnPropertyChanged(nameof(IsP1DireitaColada));
                OnPropertyChanged(nameof(IsP2EsquerdaColada));
                OnPropertyChanged(nameof(IsP2DireitaColada));
                OnPropertyChanged(nameof(IsP3EsquerdaColada));
                OnPropertyChanged(nameof(IsP3DireitaColada));
                CalcularTotal();
                OnPropertyChanged(string.Empty);
            });
        }

        private void ProcessarMudancaMedida()
        {
            string lTexto = LarguraInput.Replace(',', '.');
            string aTexto = AlturaInput.Replace(',', '.');

            if (double.TryParse(lTexto, CultureInfo.InvariantCulture, out double l))
                Peca.Largura = l;

            if (double.TryParse(aTexto, CultureInfo.InvariantCulture, out double a))
                Peca.Altura = a;

            ForcarAtualizacaoCompleta();
        }

        private void CalcularTotal()
        {
            if (PedraSelecionada == null)
                return;

            double precoM2 = PedraSelecionada.ValorPorMetro;
            double totalPedra = 0;
            double totalMaoObra = 0;
            double valorML = 0;

            double.TryParse(
                ValorMetroLinearInput.Replace(',', '.'),
                NumberStyles.Any,
                CultureInfo.InvariantCulture,
                out valorML);

            // PEÇA PRINCIPAL
            double area1 = Peca.Largura * Peca.Altura;
            double pedra1 = area1 * precoM2;
            double mao1 = Peca.Largura * valorML;

            totalPedra += pedra1;
            totalMaoObra += mao1;
            Peca.ValorTotalPeca = pedra1;

            // BANCADA EM L (P2)
            if (Peca2.Largura > 0 && Peca2.Altura > 0)
            {
                double area2 = Peca2.Largura * Peca2.Altura;
                totalPedra += area2 * precoM2;
                totalMaoObra += Peca2.Largura * valorML;
            }

            // BANCADA EM U (P3)
            if (Peca3.Largura > 0 && Peca3.Altura > 0)
            {
                double area3 = Peca3.Largura * Peca3.Altura;
                totalPedra += area3 * precoM2;
                totalMaoObra += Peca3.Largura * valorML;
            }

            int quantidadeFinal = UsarMultiplicador ? Quantidade : 1;
            ValorMaoDeObra = totalMaoObra * quantidadeFinal;
            TotalGeral = (totalPedra + totalMaoObra) * quantidadeFinal;

            OnPropertyChanged(nameof(ValorMaterial));
            OnPropertyChanged(nameof(ValorMaoDeObra));
            OnPropertyChanged(nameof(TotalGeral));
        }

        [RelayCommand]
        private async Task SalvarPeca()
        {
            if (Peca.Largura <= 0 || Peca.Altura <= 0 || PedraSelecionada == null)
            {
                await Shell.Current.DisplayAlert("Aviso", "Preencha as medidas e selecione o material!", "OK");
                return;
            }

            Peca.PedraNome = PedraSelecionada.NomeChapa;
            await Shell.Current.GoToAsync("..", new Dictionary<string, object> { { "NovaPeca", Peca } });
        }
    }
}