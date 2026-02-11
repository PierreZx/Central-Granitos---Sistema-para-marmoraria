using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Globalization;
using System.Linq; // Garante o uso do LINQ

namespace Marmorariacentral.ViewModels
{
    public partial class CalculadoraPecaViewModel : ObservableObject, IQueryAttributable
    {
        private readonly DatabaseService _dbService;

        [ObservableProperty]
        private PecaOrcamento peca = new();

        [ObservableProperty]
        private ObservableCollection<EstoqueItem> listaEstoque = new();

        [ObservableProperty]
        private EstoqueItem? pedraSelecionada; // O '?' indica que pode ser nulo

        [ObservableProperty]
        private string larguraInput = "0,00";

        [ObservableProperty]
        private string alturaInput = "0,00";

        [ObservableProperty]
        private PecaDrawable desenhoPeca = new();

        public CalculadoraPecaViewModel(DatabaseService dbService)
        {
            _dbService = dbService;
            DesenhoPeca = new PecaDrawable();
            _ = CarregarEstoque();
        }

        public void ApplyQueryAttributes(IDictionary<string, object> query)
        {
            if (query.TryGetValue("PecaParaEditar", out var pecaObj) && pecaObj is PecaOrcamento pecaEdicao)
            {
                Peca = pecaEdicao;
                LarguraInput = pecaEdicao.Largura.ToString("N2", CultureInfo.CurrentCulture);
                AlturaInput = pecaEdicao.Altura.ToString("N2", CultureInfo.CurrentCulture);
                
                // CORREÇÃO CS8601: Verificação de segurança ao buscar na lista
                if (ListaEstoque != null && ListaEstoque.Any())
                {
                    PedraSelecionada = ListaEstoque.FirstOrDefault(x => x.NomeChapa == pecaEdicao.PedraNome);
                }

                ProcessarMudancaMedida();
            }
        }

        private async Task CarregarEstoque()
        {
            try
            {
                var itens = await _dbService.GetItemsAsync<EstoqueItem>();
                MainThread.BeginInvokeOnMainThread(() =>
                {
                    ListaEstoque.Clear();
                    foreach (var item in itens) ListaEstoque.Add(item);
                    
                    // CORREÇÃO CS8601: Busca segura após carregar a lista
                    if (Peca != null && !string.IsNullOrEmpty(Peca.PedraNome))
                    {
                        var pedraEncontrada = ListaEstoque.FirstOrDefault(x => x.NomeChapa == Peca.PedraNome);
                        if (pedraEncontrada != null)
                        {
                            PedraSelecionada = pedraEncontrada;
                        }
                    }
                });
            }
            catch (Exception ex) { Debug.WriteLine(ex.Message); }
        }

        partial void OnPedraSelecionadaChanged(EstoqueItem? value) => CalcularTotal();
        partial void OnLarguraInputChanged(string value) => ProcessarMudancaMedida();
        partial void OnAlturaInputChanged(string value) => ProcessarMudancaMedida();

        private void ProcessarMudancaMedida()
        {
            string lTexto = LarguraInput.Replace(',', '.');
            string aTexto = AlturaInput.Replace(',', '.');

            if (double.TryParse(lTexto, CultureInfo.InvariantCulture, out double l))
                Peca.Largura = l;

            if (double.TryParse(aTexto, CultureInfo.InvariantCulture, out double a))
                Peca.Altura = a;

            DesenhoPeca.Largura = Peca.Largura;
            DesenhoPeca.Altura = Peca.Altura;
            
            OnPropertyChanged(nameof(DesenhoPeca));
            CalcularTotal();
        }

        private void CalcularTotal()
        {
            if (PedraSelecionada != null)
            {
                decimal area = (decimal)Peca.Largura * (decimal)Peca.Altura;
                decimal precoM2 = (decimal)PedraSelecionada.ValorPorMetro;
                
                Peca.ValorM2 = (double)precoM2;
                Peca.ValorTotalPeca = (double)(area * precoM2);
                
                OnPropertyChanged(nameof(Peca));
            }
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

            await Shell.Current.GoToAsync("..", new Dictionary<string, object> 
            { 
                { "NovaPeca", Peca } 
            });
        }
    }

    public class PecaDrawable : IDrawable
    {
        public double Largura { get; set; }
        public double Altura { get; set; }

        public void Draw(ICanvas canvas, RectF dirtyRect)
        {
            canvas.Antialias = true;
            if (Largura <= 0 || Altura <= 0) return;

            float padding = 60;
            float disponivelW = dirtyRect.Width - padding;
            float disponivelH = dirtyRect.Height - padding;

            float escalaX = disponivelW / (float)Largura;
            float escalaY = disponivelH / (float)Altura;
            float escalaFinal = Math.Min(escalaX, escalaY);

            float drawW = (float)Largura * escalaFinal;
            float drawH = (float)Altura * escalaFinal;

            float x = (dirtyRect.Width - drawW) / 2;
            float y = (dirtyRect.Height - drawH) / 2;

            canvas.FillColor = Color.FromArgb("#808080");
            canvas.FillRectangle(x, y, drawW, drawH);
            canvas.StrokeColor = Colors.Black;
            canvas.StrokeSize = 2;
            canvas.DrawRectangle(x, y, drawW, drawH);

            canvas.FontColor = Colors.Black;
            canvas.FontSize = 14;
            canvas.DrawString($"{Largura:N2}m", x, y - 15, drawW, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
            canvas.DrawString($"{Altura:N2}m", x - 60, y + (drawH / 2) - 10, 50, 20, HorizontalAlignment.Right, VerticalAlignment.Center);
        }
    }
}