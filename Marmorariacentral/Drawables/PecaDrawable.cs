using Marmorariacentral.ViewModels;
using Microsoft.Maui.Graphics;

namespace Marmorariacentral.Drawables
{
    public class PecaDrawable : IDrawable
    {
        private readonly CalculadoraPecaViewModel vm;
        private const float MARGEM = 100; 
        private readonly Color CorRodobanca = Color.FromArgb("#2E7D32");
        private readonly Color CorSaia = Color.FromArgb("#B76E00");
        private readonly Color CorRecorteBojo = Color.FromArgb("#2980B9");
        private readonly Color CorRecorteCooktop = Color.FromArgb("#C0392B");

        public PecaDrawable(CalculadoraPecaViewModel viewModel) => vm = viewModel;

        public void Draw(ICanvas canvas, RectF dirtyRect)
        {
            if (vm.Peca.Largura <= 0.01) return;

            canvas.Antialias = true;
            canvas.FillColor = Colors.White;
            canvas.FillRectangle(dirtyRect);

            double largEsq = vm.TemPernaEsquerda ? vm.Peca2.Largura : 0;
            double largDir = (vm.LadoP2 == "Direita") ? vm.Peca2.Largura : (vm.Peca3.Largura > 0.01 ? vm.Peca3.Largura : 0);
            double largTot = vm.Peca.Largura + largEsq + largDir;
            double altMax = Math.Max(vm.Peca.Altura, Math.Max(vm.Peca2.Altura, vm.Peca3.Altura));

            float escala = (float)Math.Min((dirtyRect.Width - MARGEM * 2) / largTot, (dirtyRect.Height - MARGEM * 2) / altMax);
            float x0 = (dirtyRect.Width - (float)(largTot * escala)) / 2;
            float y0 = (dirtyRect.Height - (float)(altMax * escala)) / 2;

            if (vm.TemPernaEsquerda) {
                DesenharPecaTecnica(canvas, x0, y0, (float)(largEsq * escala), (float)(vm.Peca2.Altura * escala), vm.Peca2.Largura, vm.Peca2.Altura,
                    vm.RodobancaP2Esquerda, vm.RodobancaP2Direita, vm.RodobancaP2Frente, vm.RodobancaP2Tras,
                    vm.SaiaP2Esquerda, vm.SaiaP2Direita, vm.SaiaP2Frente, vm.SaiaP2Tras, true, false, "P2", escala);
            }

            float xP1 = x0 + (float)(largEsq * escala);
            DesenharPecaTecnica(canvas, xP1, y0, (float)(vm.Peca.Largura * escala), (float)(vm.Peca.Altura * escala), vm.Peca.Largura, vm.Peca.Altura,
                vm.RodobancaP1Esquerda, vm.RodobancaP1Direita, vm.RodobancaP1Frente, vm.RodobancaP1Tras,
                vm.SaiaP1Esquerda, vm.SaiaP1Direita, vm.SaiaP1Frente, vm.SaiaP1Tras, false, false, "P1", escala);

            if (vm.TemPernaDireita) {
                bool isP2 = vm.LadoP2 == "Direita";
                float xD = xP1 + (float)(vm.Peca.Largura * escala);
                double lD = isP2 ? vm.Peca2.Largura : vm.Peca3.Largura;
                double aD = isP2 ? vm.Peca2.Altura : vm.Peca3.Altura;
                DesenharPecaTecnica(canvas, xD, y0, (float)(lD * escala), (float)(aD * escala), lD, aD,
                    isP2 ? vm.RodobancaP2Esquerda : vm.RodobancaP3Esquerda,
                    isP2 ? vm.RodobancaP2Direita : vm.RodobancaP3Direita,
                    isP2 ? vm.RodobancaP2Frente : vm.RodobancaP3Frente,
                    isP2 ? vm.RodobancaP2Tras : vm.RodobancaP3Tras,
                    isP2 ? vm.SaiaP2Esquerda : vm.SaiaP3Esquerda,
                    isP2 ? vm.SaiaP2Direita : vm.SaiaP3Direita,
                    isP2 ? vm.SaiaP2Frente : vm.SaiaP3Frente,
                    isP2 ? vm.SaiaP2Tras : vm.SaiaP3Tras, false, true, "P3", escala);
            }
        }

        private void DesenharPecaTecnica(ICanvas canvas, float x, float y, float w, float h, double realW, double realH,
            double rbE, double rbD, double rbF, double rbT, double sE, double sD, double sF, double sT, bool isEsq, bool isDir, string pecaId, float escala)
        {
            // Reset de estilo para garantir linhas sólidas na peça
            canvas.StrokeDashPattern = null; 
            canvas.FillColor = Color.FromArgb("#E8E8E8");
            canvas.FillRectangle(x, y, w, h);
            canvas.StrokeColor = Colors.Black;
            canvas.StrokeSize = 2;
            canvas.DrawRectangle(x, y, w, h);

            canvas.FontColor = Colors.Black; canvas.FontSize = 12;
            canvas.DrawString($"{realW:N2}m", x, y - 45, w, 15, HorizontalAlignment.Center, VerticalAlignment.Center);
            canvas.SaveState();
            canvas.Translate(x - 45, y + h / 2); canvas.Rotate(-90);
            canvas.DrawString($"{realH:N2}m", -h / 2, -10, h, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
            canvas.RestoreState();

            // ACABAMENTOS
            float hP1Px = (float)(vm.Peca.Altura * escala);
            DesenharLinhaAcabamento(canvas, x, y, x + w, y, rbT, sT, "T");
            DesenharLinhaAcabamento(canvas, x, y + h, x + w, y + h, rbF, sF, "F");

            if (!isDir) DesenharLinhaAcabamento(canvas, x, y, x, y + h, rbE, sE, "E");
            else if (h > hP1Px) DesenharLinhaAcabamento(canvas, x, y + hP1Px, x, y + h, rbE, sE, "E");

            if (!isEsq) DesenharLinhaAcabamento(canvas, x + w, y, x + w, y + h, rbD, sD, "D");
            else if (h > hP1Px) DesenharLinhaAcabamento(canvas, x + w, y + hP1Px, x + w, y + h, rbD, sD, "D");

            // RECORTES
            if (vm.TemBojo && vm.PecaDestinoBojo == pecaId)
                DesenharRecorteTecnico(canvas, x, y, escala, vm.LarguraBojoInput, vm.AlturaBojoInput, vm.BojoXInput, CorRecorteBojo, "BOJO");

            if (vm.TemCooktop && vm.PecaDestinoCooktop == pecaId)
                DesenharRecorteTecnico(canvas, x, y, escala, vm.LarguraCooktopInput, vm.AlturaCooktopInput, vm.CooktopXInput, CorRecorteCooktop, "COOKTOP");
        }

        private void DesenharRecorteTecnico(ICanvas canvas, float xPeca, float yPeca, float escala, string sLarg, string sAlt, string sX, Color cor, string label)
        {
            float w = (float)(ConverterParaDouble(sLarg) * escala);
            float h = (float)(ConverterParaDouble(sAlt) * escala);
            float x = xPeca + (float)(ConverterParaDouble(sX) * escala);
            float y = yPeca + 10;

            canvas.StrokeColor = cor;
            canvas.StrokeSize = 2;
            canvas.StrokeDashPattern = new float[] { 4, 2 }; // Define tracejado apenas para o recorte
            canvas.DrawRectangle(x, y, w, h);

            canvas.FontColor = cor; canvas.FontSize = 9;
            canvas.DrawString(label, x, y, w, h, HorizontalAlignment.Center, VerticalAlignment.Center);
            canvas.DrawString($"{ConverterParaDouble(sLarg):N2}x{ConverterParaDouble(sAlt):N2}", x, y + h + 2, w, 12, HorizontalAlignment.Center, VerticalAlignment.Top);
            
            canvas.StrokeDashPattern = null; // Reseta o tracejado imediatamente após desenhar o recorte
        }

        private void DesenharLinhaAcabamento(ICanvas canvas, float x1, float y1, float x2, float y2, double rb, double saia, string pos)
        {
            canvas.StrokeDashPattern = null; // Garante linha sólida
            float midX = (x1 + x2) / 2; float midY = (y1 + y2) / 2;
            if (rb > 0.001) {
                canvas.StrokeColor = CorRodobanca; canvas.StrokeSize = 4;
                canvas.DrawLine(x1, y1, x2, y2);
                canvas.FontColor = CorRodobanca; canvas.FontSize = 10;
                float offY = (pos == "T") ? -22 : (pos == "F") ? 22 : 0;
                float offX = (pos == "E") ? -35 : (pos == "D") ? 35 : 0;
                canvas.DrawString($"{rb:N2}", midX - 15 + offX, midY - 7 + offY, 30, 15, HorizontalAlignment.Center, VerticalAlignment.Center);
            }
            if (saia > 0.001) {
                canvas.StrokeColor = CorSaia; canvas.StrokeSize = 3;
                float lineOff = rb > 0 ? 5 : 0; canvas.DrawLine(x1 + lineOff, y1 + lineOff, x2 - lineOff, y2 - lineOff);
                canvas.FontColor = CorSaia; canvas.FontSize = 10;
                float offY = (pos == "T") ? 18 : (pos == "F") ? -18 : 0;
                float offX = (pos == "E") ? 25 : (pos == "D") ? -25 : 0;
                canvas.DrawString($"{saia:N2}", midX - 15 + offX, midY - 7 + offY, 30, 15, HorizontalAlignment.Center, VerticalAlignment.Center);
            }
        }

        private double ConverterParaDouble(string valor) {
            if (string.IsNullOrWhiteSpace(valor)) return 0;
            return double.TryParse(valor.Replace(',', '.'), System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double r) ? r : 0;
        }
    }
}