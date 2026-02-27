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
    [QueryProperty(nameof(ClienteSelecionado), "ClienteSelecionado")]
    [QueryProperty(nameof(PecaParaEditar), "PecaParaEditar")]
    public partial class CalculadoraPecaViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;

        // ==========================================
        // OBJETOS DE DADOS E ESTADO
        // ==========================================
        [ObservableProperty] private Cliente clienteSelecionado;
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

        // INPUTS DE TEXTO COM INTERCEPTADORES
        [ObservableProperty] private string larguraInput = "0,00";
        [ObservableProperty] private string alturaInput = "0,00";
        [ObservableProperty] private string larguraP2Input = "0,00";
        [ObservableProperty] private string alturaP2Input = "0,00";
        [ObservableProperty] private string larguraP3Input = "0,00";
        [ObservableProperty] private string alturaP3Input = "0,00";
        [ObservableProperty] private string valorMetroLinearInput = "130";
        [ObservableProperty] private string quantidadeInput = "1";
        [ObservableProperty] private bool usarMultiplicador = false;

        // Ganchos de interceptação (Sincronização em Tempo Real)
        partial void OnLarguraInputChanged(string value) { Peca.Largura = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnAlturaInputChanged(string value) { Peca.Altura = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnLarguraP2InputChanged(string value) { Peca.LarguraP2 = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnAlturaP2InputChanged(string value) { Peca.AlturaP2 = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnLarguraP3InputChanged(string value) { Peca.LarguraP3 = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnAlturaP3InputChanged(string value) { Peca.AlturaP3 = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnValorMetroLinearInputChanged(string value) { Peca.ValorMetroLinear = ConverterParaDouble(value); NotificarMudanca(); }
        partial void OnQuantidadeInputChanged(string value) => NotificarMudanca();

        public int Quantidade => int.TryParse(QuantidadeInput, out int q) ? Math.Max(q, 1) : 1;
        public double ValorTotalPeca => TotalGeral;

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
        // RODOBANCA (VALORES PADRÃO PARA NOVAS PEÇAS)
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
        // SAIA (VALORES PADRÃO PARA NOVAS PEÇAS)
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

        public bool TemPernaEsquerda => Peca.LarguraP2 > 0.01 && LadoP2 == "Esquerda";
        public bool TemPernaDireita => (Peca.LarguraP2 > 0.01 && LadoP2 == "Direita") || (Peca.LarguraP3 > 0.01);
        public IDrawable DesenhoPeca { get; }

        public CalculadoraPecaViewModel(DatabaseService dbService)
        {
            _dbService = dbService;
            DesenhoPeca = new PecaDrawable(this);
            _ = CarregarEstoque();
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
            if (string.IsNullOrWhiteSpace(valor)) return 0;
            return double.TryParse(valor.Replace(',', '.'), NumberStyles.Any, CultureInfo.InvariantCulture, out double result) ? result : 0;
        }

        private void CalcularTotal()
        {
            if (PedraSelecionada == null) return;
            double areaTotal = (Peca.Largura * Peca.Altura) + (Peca.LarguraP2 * Peca.AlturaP2) + (Peca.LarguraP3 * Peca.AlturaP3);
            TotalGeral = ((areaTotal * PedraSelecionada.ValorPorMetro) + ((Peca.Largura + Peca.LarguraP2 + Peca.LarguraP3) * ConverterParaDouble(ValorMetroLinearInput))) * Quantidade;
        }

        // ==========================================
        // NAVEGAÇÃO DE ABAS
        // ==========================================
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

                LarguraInput = edicao.Largura.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                AlturaInput = edicao.Altura.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                LarguraP2Input = edicao.LarguraP2.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                AlturaP2Input = edicao.AlturaP2.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                LadoP2 = edicao.LadoP2 ?? "Esquerda";
                LarguraP3Input = edicao.LarguraP3.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                AlturaP3Input = edicao.AlturaP3.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                LadoP3 = edicao.LadoP3 ?? "Direita";
                ValorMetroLinearInput = edicao.ValorMetroLinear.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                QuantidadeInput = edicao.Quantidade.ToString();
                UsarMultiplicador = edicao.UsarMultiplicador;

                // CORREÇÃO: Sobrescreve os valores padrão com o que está no banco (resolve o bug do "0" voltar a ser "0.10")
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
                LarguraBojoInput = edicao.LarguraBojo.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                AlturaBojoInput = edicao.AlturaBojo.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                BojoXInput = edicao.BojoX.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                TemCooktop = edicao.TemCooktop; PecaDestinoCooktop = edicao.PecaDestinoCooktop ?? "P1";
                LarguraCooktopInput = edicao.LarguraCooktop.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                AlturaCooktopInput = edicao.AlturaCooktop.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');
                CooktopXInput = edicao.CooktopX.ToString("N2", CultureInfo.InvariantCulture).Replace('.', ',');

                await Task.Delay(150);
                NotificarMudanca();
            }
        }

        [RelayCommand]
        private async Task SalvarPeca()
        {
            if (PedraSelecionada == null) { await Shell.Current.DisplayAlert("Aviso", "Selecione o material!", "OK"); return; }
            
            // SINCRONIZAÇÃO FINAL: Garante que os acabamentos editados sejam salvos na Peça
            Peca.PedraNome = PedraSelecionada.NomeChapa; Peca.ValorM2 = PedraSelecionada.ValorPorMetro;
            Peca.Largura = ConverterParaDouble(LarguraInput); Peca.Altura = ConverterParaDouble(AlturaInput);
            Peca.RodobancaP1Esquerda = RodobancaP1Esquerda; Peca.RodobancaP1Direita = RodobancaP1Direita;
            Peca.RodobancaP1Frente = RodobancaP1Frente; Peca.RodobancaP1Tras = RodobancaP1Tras;
            Peca.SaiaP1Frente = SaiaP1Frente; // Sincroniza a saia frontal padrão
            
            Peca.Quantidade = Quantidade; Peca.ValorTotalPeca = TotalGeral;
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