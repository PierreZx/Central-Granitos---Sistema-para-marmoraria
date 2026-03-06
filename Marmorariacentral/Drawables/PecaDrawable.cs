using Marmorariacentral.ViewModels;
using Microsoft.Maui.Graphics;

namespace Marmorariacentral.Drawables
{
    public class PecaDrawable : IDrawable
    {
        private readonly CalculadoraPecaViewModel vm;
        private const float MARGEM = 60; 
        private const float ESPACO_EXPLODIDO = 40; // Espaço para as setas entre peças
        
        private readonly Color CorRodobanca = Color.FromArgb("#2E7D32"); // Verde
        private readonly Color CorSaia = Color.FromArgb("#B76E00");      // Laranja/Ouro
        private readonly Color CorRecorteBojo = Color.FromArgb("#2980B9");
        private readonly Color CorRecorteCooktop = Color.FromArgb("#C0392B");
        private readonly Color CorSeta = Color.FromArgb("#555555");

        public PecaDrawable(CalculadoraPecaViewModel viewModel) => vm = viewModel;

        public void Draw(ICanvas canvas, RectF dirtyRect)
        {
            if (vm.Peca == null || vm.Peca.Largura <= 0.01) return;

            canvas.Antialias = true;
            canvas.FillColor = Colors.White;
            canvas.FillRectangle(dirtyRect);

            // Cálculo de dimensões totais considerando os espaços da vista explodida
            double largEsq = vm.TemPernaEsquerda ? vm.Peca.LarguraP2 : 0;
            double largDir = (vm.LadoP2 == "Direita") ? vm.Peca.LarguraP2 : (vm.Peca.LarguraP3 > 0.01 ? vm.Peca.LarguraP3 : 0);
            
            // Soma os espaços explodidos se houver pernas
            float espacosAdicionais = 0;
            if (vm.TemPernaEsquerda) espacosAdicionais += ESPACO_EXPLODIDO;
            if (vm.TemPernaDireita) espacosAdicionais += ESPACO_EXPLODIDO;

            double largTotReal = vm.Peca.Largura + largEsq + largDir;
            double altMax = Math.Max(vm.Peca.Altura, Math.Max(vm.Peca.AlturaP2, vm.Peca.AlturaP3));

            // Calcula escala garantindo que as setas e margens caibam
            float escala = (float)Math.Min((dirtyRect.Width - (MARGEM * 2) - espacosAdicionais) / largTotReal, 
                                          (dirtyRect.Height - MARGEM * 2) / altMax);
            
            float x0 = (dirtyRect.Width - (float)(largTotReal * escala) - espacosAdicionais) / 2;
            float y0 = (dirtyRect.Height - (float)(altMax * escala)) / 2;

            float currentX = x0;

            // 1. Desenha Perna Esquerda (P2)
            if (vm.TemPernaEsquerda) {
                float wP2 = (float)(vm.Peca.LarguraP2 * escala);
                float hP2 = (float)(vm.Peca.AlturaP2 * escala);
                
                DesenharPecaTecnica(canvas, currentX, y0, wP2, hP2, vm.Peca.LarguraP2, vm.Peca.AlturaP2,
                    vm.RodobancaP2Esquerda, vm.RodobancaP2Direita, vm.RodobancaP2Frente, vm.RodobancaP2Tras,
                    vm.SaiaP2Esquerda, vm.SaiaP2Direita, vm.SaiaP2Frente, vm.SaiaP2Tras, true, false, "P2", escala);

                // Seta de Conexão P2 -> P1
                DesenharSetaConexao(canvas, currentX + wP2, y0 + (hP2 / 2), currentX + wP2 + ESPACO_EXPLODIDO, y0 + (hP2 / 2));
                
                currentX += wP2 + ESPACO_EXPLODIDO;
            }

            // 2. Desenha Peça Principal (P1)
            float wP1 = (float)(vm.Peca.Largura * escala);
            float hP1 = (float)(vm.Peca.Altura * escala);
            DesenharPecaTecnica(canvas, currentX, y0, wP1, hP1, vm.Peca.Largura, vm.Peca.Altura,
                vm.RodobancaP1Esquerda, vm.RodobancaP1Direita, vm.RodobancaP1Frente, vm.RodobancaP1Tras,
                vm.SaiaP1Esquerda, vm.SaiaP1Direita, vm.SaiaP1Frente, vm.SaiaP1Tras, false, false, "P1", escala);

            float lastXP1 = currentX + wP1;
            currentX += wP1;

            // 3. Desenha Perna Direita (P2 ou P3)
            if (vm.TemPernaDireita) {
                currentX += ESPACO_EXPLODIDO;
                bool isP2 = vm.LadoP2 == "Direita";
                double lD = isP2 ? vm.Peca.LarguraP2 : vm.Peca.LarguraP3;
                double aD = isP2 ? vm.Peca.AlturaP2 : vm.Peca.AlturaP3;
                float wD = (float)(lD * escala);
                float hD = (float)(aD * escala);

                // Seta de Conexão P1 -> P3
                DesenharSetaConexao(canvas, lastXP1, y0 + (hD / 2), lastXP1 + ESPACO_EXPLODIDO, y0 + (hD / 2));

                DesenharPecaTecnica(canvas, currentX, y0, wD, hD, lD, aD,
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

        private void DesenharSetaConexao(ICanvas canvas, float x1, float y1, float x2, float y2)
        {
            canvas.StrokeColor = CorSeta;
            canvas.StrokeSize = 1;
            canvas.StrokeDashPattern = new float[] { 4, 4 };
            canvas.DrawLine(x1, y1, x2, y2);
            
            // Cabeça da seta simples
            canvas.StrokeDashPattern = null;
            canvas.DrawLine(x2 - 5, y1 - 5, x2, y1);
            canvas.DrawLine(x2 - 5, y1 + 5, x2, y1);
            canvas.DrawLine(x1 + 5, y1 - 5, x1, y1);
            canvas.DrawLine(x1 + 5, y1 + 5, x1, y1);
        }

        private void DesenharPecaTecnica(ICanvas canvas, float x, float y, float w, float h, double realW, double realH,
            double rbE, double rbD, double rbF, double rbT, double sE, double sD, double sF, double sT, bool isEsq, bool isDir, string pecaId, float escala)
        {
            canvas.FillColor = Color.FromArgb("#F5F5F5");
            canvas.FillRectangle(x, y, w, h);
            canvas.StrokeColor = Colors.Black;
            canvas.StrokeSize = 1.5f;
            canvas.DrawRectangle(x, y, w, h);

            canvas.FontColor = Colors.Black; 
            canvas.FontSize = 11; 
            
            // Nome da Peça centralizado
            canvas.DrawString(pecaId, x, y + (h/2) - 10, w, 20, HorizontalAlignment.Center, VerticalAlignment.Center);

            // Medidas principais
            canvas.DrawString($"{realW:N2}m", x, y - 25, w, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
            
            canvas.SaveState();
            canvas.Translate(x - 30, y + h / 2); 
            canvas.Rotate(-90);
            canvas.DrawString($"{realH:N2}m", -h / 2, 0, h, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
            canvas.RestoreState();

            // Desenho dos Acabamentos (Rodobancas e Saias)
            DesenharLinhaAcabamento(canvas, x, y, x + w, y, rbT, sT, "T"); // Trás
            DesenharLinhaAcabamento(canvas, x, y + h, x + w, y + h, rbF, sF, "F"); // Frente
            DesenharLinhaAcabamento(canvas, x, y, x, y + h, rbE, sE, "E"); // Esquerda
            DesenharLinhaAcabamento(canvas, x + w, y, x + w, y + h, rbD, sD, "D"); // Direita

            // Recortes (Cozinha/Cooktop)
            if (vm.TemBojo && vm.PecaDestinoBojo == pecaId)
                DesenharRecorteTecnico(canvas, x, y, escala, vm.LarguraBojoInput, vm.AlturaBojoInput, vm.BojoXInput, CorRecorteBojo, "CUBA");

            if (vm.TemCooktop && vm.PecaDestinoCooktop == pecaId)
                DesenharRecorteTecnico(canvas, x, y, escala, vm.LarguraCooktopInput, vm.AlturaCooktopInput, vm.CooktopXInput, CorRecorteCooktop, "COOKTOP");
        }

        private void DesenharRecorteTecnico(ICanvas canvas, float xPeca, float yPeca, float escala, string sLarg, string sAlt, string sX, Color cor, string label)
        {
            float w = (float)(ConverterParaDouble(sLarg) * escala);
            float h = (float)(ConverterParaDouble(sAlt) * escala);
            float x = xPeca + (float)(ConverterParaDouble(sX) * escala);
            float y = yPeca + (float)(0.10 * escala); // Afastado da borda superior

            canvas.StrokeColor = cor;
            canvas.StrokeSize = 2;
            canvas.StrokeDashPattern = new float[] { 6, 3 }; 
            canvas.DrawRectangle(x, y, w, h);

            canvas.FontColor = cor; 
            canvas.FontSize = 9;
            canvas.DrawString(label, x, y + (h/2) - 10, w, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
            canvas.DrawString($"{ConverterParaDouble(sLarg):N2}x{ConverterParaDouble(sAlt):N2}", x, y + h + 2, w, 15, HorizontalAlignment.Center, VerticalAlignment.Top);
            canvas.StrokeDashPattern = null; 
        }

        private void DesenharLinhaAcabamento(ICanvas canvas, float x1, float y1, float x2, float y2, double rb, double saia, string pos)
        {
            float midX = (x1 + x2) / 2; float midY = (y1 + y2) / 2;
            
            // Rodobanca (Verde)
            if (rb > 0.001) {
                canvas.StrokeColor = CorRodobanca; 
                canvas.StrokeSize = 5;
                canvas.DrawLine(x1, y1, x2, y2);
                
                canvas.FontColor = CorRodobanca; canvas.FontSize = 10;
                float offY = (pos == "T") ? -18 : (pos == "F") ? 20 : 0;
                float offX = (pos == "E") ? -30 : (pos == "D") ? 30 : 0;
                canvas.DrawString($"R:{rb:N2}", midX - 20 + offX, midY - 10 + offY, 40, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
            }
            
            // Saia (Laranja)
            if (saia > 0.001) {
                canvas.StrokeColor = CorSaia; 
                canvas.StrokeSize = 3;
                // Pequeno recuo para a saia não sumir sob a rodobanca
                float shift = (rb > 0.001) ? 5 : 0;
                canvas.DrawLine(x1 + shift, y1 + shift, x2 - shift, y2 - shift);
                
                canvas.FontColor = CorSaia; canvas.FontSize = 10;
                float offY = (pos == "T") ? 12 : (pos == "F") ? -12 : 0;
                float offX = (pos == "E") ? 20 : (pos == "D") ? -20 : 0;
                canvas.DrawString($"S:{saia:N2}", midX - 20 + offX, midY - 10 + offY, 40, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
            }
        }

        private double ConverterParaDouble(string valor) => 
            double.TryParse(valor?.Replace(',', '.'), System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double r) ? r : 0;
    }
}