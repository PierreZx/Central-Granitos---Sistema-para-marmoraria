using Marmorariacentral.ViewModels;
using Microsoft.Maui.Graphics;

namespace Marmorariacentral.Drawables
{
    // Interface de abstração para operações de desenho - APENAS SETTERS
    public interface IDrawingCanvas
    {
        bool Antialias { set; }
        Color StrokeColor { set; }
        Color FillColor { set; }
        Color FontColor { set; }
        float StrokeSize { set; }
        float FontSize { set; }
        float[] StrokeDashPattern { set; }

        void DrawLine(float x1, float y1, float x2, float y2);
        void DrawRectangle(float x, float y, float width, float height);
        void FillRectangle(float x, float y, float width, float height);
        void DrawString(string value, float x, float y, float width, float height, 
            HorizontalAlignment horizontalAlignment, VerticalAlignment verticalAlignment);
        void DrawString(string value, float x, float y, HorizontalAlignment horizontalAlignment);
        void SaveState();
        void RestoreState();
        void Translate(float tx, float ty);
        void Rotate(float degrees);
    }

    // Adaptador para MAUI ICanvas - APENAS SETTERS
    public class MauiCanvasAdapter : IDrawingCanvas
    {
        private readonly ICanvas _canvas;

        public MauiCanvasAdapter(ICanvas canvas)
        {
            _canvas = canvas;
        }

        public bool Antialias 
        { 
            set => _canvas.Antialias = value; 
        }

        public Color StrokeColor 
        { 
            set => _canvas.StrokeColor = value; 
        }

        public Color FillColor 
        { 
            set => _canvas.FillColor = value; 
        }

        public Color FontColor 
        { 
            set => _canvas.FontColor = value; 
        }

        public float StrokeSize 
        { 
            set => _canvas.StrokeSize = value; 
        }

        public float FontSize 
        { 
            set => _canvas.FontSize = value; 
        }

        public float[] StrokeDashPattern 
        { 
            set => _canvas.StrokeDashPattern = value; 
        }

        public void DrawLine(float x1, float y1, float x2, float y2) => 
            _canvas.DrawLine(x1, y1, x2, y2);

        public void DrawRectangle(float x, float y, float width, float height) => 
            _canvas.DrawRectangle(x, y, width, height);

        public void FillRectangle(float x, float y, float width, float height) => 
            _canvas.FillRectangle(x, y, width, height);

        public void DrawString(string value, float x, float y, float width, float height, 
            HorizontalAlignment horizontalAlignment, VerticalAlignment verticalAlignment) =>
            _canvas.DrawString(value, x, y, width, height, horizontalAlignment, verticalAlignment);

        public void DrawString(string value, float x, float y, HorizontalAlignment horizontalAlignment) =>
            _canvas.DrawString(value, x, y, horizontalAlignment);

        public void SaveState() => _canvas.SaveState();
        public void RestoreState() => _canvas.RestoreState();
        public void Translate(float tx, float ty) => _canvas.Translate(tx, ty);
        public void Rotate(float degrees) => _canvas.Rotate(degrees);
    }

    public class PecaDrawable : IDrawable
    {
        private readonly CalculadoraPecaViewModel vm;
        private const float PERCENTUAL_APROVEITAMENTO = 0.95f; 
        private const float ESPACO_EXPLODIDO = 45; 
        private const float LIMIAR_ACABAMENTO = 0.001f; // Valor mínimo para considerar acabamento presente

        private readonly Color CorRodobanca = Color.FromArgb("#2E7D32"); // Verde
        private readonly Color CorSaia = Color.FromArgb("#B76E00");      // Laranja/Ouro
        private readonly Color CorRecorteBojo = Color.FromArgb("#2980B9");
        private readonly Color CorRecorteCooktop = Color.FromArgb("#C0392B");
        private readonly Color CorSeta = Color.FromArgb("#555555");

        // Propriedade para controlar se o desenho é explodido ou unido
        public bool IsVistaExplodida { get; set; } = false;

        public PecaDrawable(CalculadoraPecaViewModel viewModel) => vm = viewModel;

        public void Draw(IDrawingCanvas canvas, RectF dirtyRect)
        {
            if (vm?.Peca == null)
                return;

            if (dirtyRect.Width <= 0 || dirtyRect.Height <= 0)
                return;

            canvas.Antialias = true;
            canvas.FillColor = Colors.White;
            canvas.FillRectangle(dirtyRect.X, dirtyRect.Y, dirtyRect.Width, dirtyRect.Height);

            if (dirtyRect.Width < 50 || dirtyRect.Height < 50)
            return;

            if (IsVistaExplodida)
            {
                DesenharVistaExplodida(canvas, dirtyRect);
            }
            else
            {
                DesenharPecaUnida(canvas, dirtyRect);
            }
        }

        // Método de compatibilidade para manter a interface IDrawable original
        public void Draw(ICanvas canvas, RectF dirtyRect)
        {
            canvas.FillColor = Colors.White;
            canvas.FillRectangle(dirtyRect);

            if (dirtyRect.Width < 1 || dirtyRect.Height < 1)
                return;

            canvas.StrokeDashPattern = null;

            var adapter = new MauiCanvasAdapter(canvas);
            Draw(adapter, dirtyRect);
        }

        private void DesenharPecaUnida(IDrawingCanvas canvas, RectF dirtyRect)
        {
            bool p2Esquerda = vm.TemPernaEsquerda && vm.LadoP2 == "Esquerda";
            bool p2Direita = vm.TemPernaDireita && vm.LadoP2 == "Direita";

            bool p3Esquerda = vm.TemPernaEsquerda && vm.LadoP2 == "Direita" && vm.Peca.LarguraP3 > LIMIAR_ACABAMENTO;
            bool p3Direita = vm.TemPernaDireita && vm.LadoP2 == "Esquerda" && vm.Peca.LarguraP3 > LIMIAR_ACABAMENTO;

            double largEsq = 0;
            double largDir = 0;

            if (p2Esquerda) largEsq = vm.Peca.LarguraP2;
            if (p3Esquerda) largEsq = vm.Peca.LarguraP3;

            if (p2Direita) largDir = vm.Peca.LarguraP2;
            if (p3Direita) largDir = vm.Peca.LarguraP3;

            double largTotReal = vm.Peca.Largura + largEsq + largDir;

            double altMax = Math.Max(vm.Peca.Altura,
                Math.Max(vm.Peca.AlturaP2, vm.Peca.AlturaP3));

            float escala = CalcularEscalaUnida(dirtyRect, largTotReal, altMax);

            float x0 = dirtyRect.X + (dirtyRect.Width - (float)(largTotReal * escala)) / 2;
            float y0 = dirtyRect.Y + (dirtyRect.Height - (float)(altMax * escala)) / 2;

            float currentX = x0;

            // PERNA ESQUERDA
            if (largEsq > 0)
            {
                bool isP2 = p2Esquerda;

                double l = isP2 ? vm.Peca.LarguraP2 : vm.Peca.LarguraP3;
                double a = isP2 ? vm.Peca.AlturaP2 : vm.Peca.AlturaP3;

                float w = (float)(l * escala);
                float h = (float)(a * escala);

                DesenharPecaUnica(
                    canvas,
                    currentX,
                    y0,
                    w,
                    h,
                    l,
                    a,

                    isP2 ? vm.RodobancaP2Esquerda : vm.RodobancaP3Esquerda,
                    isP2 ? vm.RodobancaP2Direita : vm.RodobancaP3Direita,
                    isP2 ? vm.RodobancaP2Frente : vm.RodobancaP3Frente,
                    isP2 ? vm.RodobancaP2Tras : vm.RodobancaP3Tras,

                    isP2 ? vm.SaiaP2Esquerda : vm.SaiaP3Esquerda,
                    isP2 ? vm.SaiaP2Direita : vm.SaiaP3Direita,
                    isP2 ? vm.SaiaP2Frente : vm.SaiaP3Frente,
                    isP2 ? vm.SaiaP2Tras : vm.SaiaP3Tras,

                    isP2 ? "P2" : "P3",
                    escala
                );

                currentX += w;
            }

            // P1
            float wP1 = (float)(vm.Peca.Largura * escala);
            float hP1 = (float)(vm.Peca.Altura * escala);

            DesenharPecaUnica(
                canvas,
                currentX,
                y0,
                wP1,
                hP1,
                vm.Peca.Largura,
                vm.Peca.Altura,

                vm.RodobancaP1Esquerda,
                vm.RodobancaP1Direita,
                vm.RodobancaP1Frente,
                vm.RodobancaP1Tras,

                vm.SaiaP1Esquerda,
                vm.SaiaP1Direita,
                vm.SaiaP1Frente,
                vm.SaiaP1Tras,

                "P1",
                escala
            );

            currentX += wP1;

            // PERNA DIREITA
            if (largDir > 0)
            {
                bool isP2 = p2Direita;

                double l = isP2 ? vm.Peca.LarguraP2 : vm.Peca.LarguraP3;
                double a = isP2 ? vm.Peca.AlturaP2 : vm.Peca.AlturaP3;

                float w = (float)(l * escala);
                float h = (float)(a * escala);

                DesenharPecaUnica(
                    canvas,
                    currentX,
                    y0,
                    w,
                    h,
                    l,
                    a,

                    isP2 ? vm.RodobancaP2Esquerda : vm.RodobancaP3Esquerda,
                    isP2 ? vm.RodobancaP2Direita : vm.RodobancaP3Direita,
                    isP2 ? vm.RodobancaP2Frente : vm.RodobancaP3Frente,
                    isP2 ? vm.RodobancaP2Tras : vm.RodobancaP3Tras,

                    isP2 ? vm.SaiaP2Esquerda : vm.SaiaP3Esquerda,
                    isP2 ? vm.SaiaP2Direita : vm.SaiaP3Direita,
                    isP2 ? vm.SaiaP2Frente : vm.SaiaP3Frente,
                    isP2 ? vm.SaiaP2Tras : vm.SaiaP3Tras,

                    isP2 ? "P2" : "P3",
                    escala
                );
            }
        }

        private void DesenharVistaExplodida(IDrawingCanvas canvas, RectF dirtyRect)
        {
            double largEsq = vm.TemPernaEsquerda ? vm.Peca.LarguraP2 : 0;
            double largDir = (vm.LadoP2 == "Direita") ? vm.Peca.LarguraP2 : (vm.Peca.LarguraP3 > LIMIAR_ACABAMENTO ? vm.Peca.LarguraP3 : 0);
            double largTotReal = vm.Peca.Largura + largEsq + largDir;
            double altMax = Math.Max(vm.Peca.Altura, Math.Max(vm.Peca.AlturaP2, vm.Peca.AlturaP3));

            float espacosAdicionais = 0;
            if (vm.TemPernaEsquerda) espacosAdicionais += ESPACO_EXPLODIDO;
            if (vm.TemPernaDireita) espacosAdicionais += ESPACO_EXPLODIDO;

            float escala = CalcularEscalaExplodida(dirtyRect, largTotReal, altMax, espacosAdicionais);
            float x0 = (dirtyRect.Width - (float)(largTotReal * escala) - espacosAdicionais) / 2;
            float y0 = (dirtyRect.Height - (float)(altMax * escala)) / 2;

            float currentX = x0;

            // Perna Esquerda (P2) - Explodida
            if (vm.TemPernaEsquerda)
            {
                float wP2 = (float)(vm.Peca.LarguraP2 * escala);
                float hP2 = (float)(vm.Peca.AlturaP2 * escala);

                DesenharPecaExplodida(canvas, currentX, y0, wP2, hP2, vm.Peca.LarguraP2, vm.Peca.AlturaP2,
                    vm.RodobancaP2Esquerda, vm.RodobancaP2Direita, vm.RodobancaP2Frente, vm.RodobancaP2Tras,
                    vm.SaiaP2Esquerda, vm.SaiaP2Direita, vm.SaiaP2Frente, vm.SaiaP2Tras, "P2", escala);

                DesenharSetaConexao(canvas, currentX + wP2, y0 + (hP2 / 2), currentX + wP2 + ESPACO_EXPLODIDO, y0 + (hP2 / 2));
                currentX += wP2 + ESPACO_EXPLODIDO;
            }

            // Peça Principal (P1) - Explodida
            float wP1 = (float)(vm.Peca.Largura * escala);
            float hP1 = (float)(vm.Peca.Altura * escala);
            float lastXP1 = currentX + wP1;

            DesenharPecaExplodida(canvas, currentX, y0, wP1, hP1, vm.Peca.Largura, vm.Peca.Altura,
                vm.RodobancaP1Esquerda, vm.RodobancaP1Direita, vm.RodobancaP1Frente, vm.RodobancaP1Tras,
                vm.SaiaP1Esquerda, vm.SaiaP1Direita, vm.SaiaP1Frente, vm.SaiaP1Tras, "P1", escala);

            currentX += wP1;

            // Perna Direita (P2 ou P3) - Explodida
            if (vm.TemPernaDireita)
            {
                bool isP2 = vm.LadoP2 == "Direita";
                double lD = isP2 ? vm.Peca.LarguraP2 : vm.Peca.LarguraP3;
                double aD = isP2 ? vm.Peca.AlturaP2 : vm.Peca.AlturaP3;
                float wD = (float)(lD * escala);
                float hD = (float)(aD * escala);

                DesenharSetaConexao(canvas, lastXP1, y0 + (hD / 2), lastXP1 + ESPACO_EXPLODIDO, y0 + (hD / 2));
                currentX = lastXP1 + ESPACO_EXPLODIDO;

                DesenharPecaExplodida(canvas, currentX, y0, wD, hD, lD, aD,
                    isP2 ? vm.RodobancaP2Esquerda : vm.RodobancaP3Esquerda,
                    isP2 ? vm.RodobancaP2Direita : vm.RodobancaP3Direita,
                    isP2 ? vm.RodobancaP2Frente : vm.RodobancaP3Frente,
                    isP2 ? vm.RodobancaP2Tras : vm.RodobancaP3Tras,
                    isP2 ? vm.SaiaP2Esquerda : vm.SaiaP3Esquerda,
                    isP2 ? vm.SaiaP2Direita : vm.SaiaP3Direita,
                    isP2 ? vm.SaiaP2Frente : vm.SaiaP3Frente,
                    isP2 ? vm.SaiaP2Tras : vm.SaiaP3Tras,
                    isP2 ? "P2" : "P3", escala);
            }
        }

        private float CalcularEscalaUnida(RectF dirtyRect, double larguraTotal, double alturaMax)
        {
            if (larguraTotal <= 0 || alturaMax <= 0)
                return 1f;

            float margem = 40f;

            float larguraDisponivel = dirtyRect.Width - margem;
            float alturaDisponivel = dirtyRect.Height - margem;

            float escalaLargura = larguraDisponivel / (float)larguraTotal;
            float escalaAltura = alturaDisponivel / (float)alturaMax;

            float escala = Math.Min(escalaLargura, escalaAltura);

            return AjustarEscala(escala);
        }

        private float CalcularEscalaExplodida(RectF dirtyRect, double larguraTotal, double alturaMax, float espacosAdicionais)
        {
            if (larguraTotal <= 0 || alturaMax <= 0)
                return 1f;

            float margem = 40f;

            float larguraDisponivel = dirtyRect.Width - margem - espacosAdicionais;
            float alturaDisponivel = dirtyRect.Height - margem;

            float escalaLargura = larguraDisponivel / (float)larguraTotal;
            float escalaAltura = alturaDisponivel / (float)alturaMax;

            float escala = Math.Min(escalaLargura, escalaAltura);

            return AjustarEscala(escala);
        }

        private float AjustarEscala(float escala)
        {
            if (float.IsNaN(escala) || float.IsInfinity(escala))
                return 1f;

            if (escala <= 0)
                return 1f;

            if (escala < 0.05f)
                return 0.05f;

            if (escala > 200f)
                return 200f;

            return escala;
        }
        private void DesenharPecaUnica(IDrawingCanvas canvas, float x, float y, float w, float h,
            double realW, double realH, double rbE, double rbD, double rbF, double rbT,
            double sE, double sD, double sF, double sT, string pecaId, float escala)
        {
            // Fundo da peça
            canvas.FillColor = Color.FromArgb("#F5F5F5");
            canvas.FillRectangle(x, y, w, h);
            canvas.StrokeColor = Colors.Black;
            canvas.StrokeSize = 1.5f;
            canvas.DrawRectangle(x, y, w, h);

            // Identificador da peça
            canvas.FontColor = Colors.Black;
            canvas.FontSize = 11;
            canvas.DrawString(pecaId, x, y + (h / 2) - 10, w, 20, HorizontalAlignment.Center, VerticalAlignment.Center);

            // Medidas
            canvas.FontSize = 9;
            canvas.DrawString($"{realW:F2}m", x, y - 18, w, 15, HorizontalAlignment.Center, VerticalAlignment.Center);

            canvas.SaveState();
            canvas.Translate(x - 18, y + h / 2);
            canvas.Rotate(-90);
            canvas.DrawString($"{realH:F2}m", -h / 2, 0, h, 15, HorizontalAlignment.Center, VerticalAlignment.Center);
            canvas.RestoreState();

            // Acabamentos colados na peça
            DesenharAcabamentoColado(canvas, x, y, x + w, y, rbT, "T");
            DesenharAcabamentoColado(canvas, x, y + h, x + w, y + h, rbF, "F");
            DesenharAcabamentoColado(canvas, x, y, x, y + h, rbE, "E");
            DesenharAcabamentoColado(canvas, x + w, y, x + w, y + h, rbD, "D");

            // Saia colada
            DesenharSaiaColada(canvas, x, y + h, x + w, y + h, sF, "F");
            DesenharSaiaColada(canvas, x, y, x, y + h, sE, "E");
            DesenharSaiaColada(canvas, x + w, y, x + w, y + h, sD, "D");
            DesenharSaiaColada(canvas, x, y, x + w, y, sT, "T");

            // Recortes
            DesenharRecortes(canvas, x, y, escala, pecaId);
        }

        private void DesenharPecaExplodida(IDrawingCanvas canvas, float x, float y, float w, float h,
            double realW, double realH, double rbE, double rbD, double rbF, double rbT,
            double sE, double sD, double sF, double sT, string pecaId, float escala)
        {
            // Fundo da peça
            canvas.FillColor = Color.FromArgb("#F5F5F5");
            canvas.FillRectangle(x, y, w, h);
            canvas.StrokeColor = Colors.Black;
            canvas.StrokeSize = 1.5f;
            canvas.DrawRectangle(x, y, w, h);

            // Identificador da peça
            canvas.FontColor = Colors.Black;
            canvas.FontSize = 11;
            canvas.DrawString(pecaId, x, y + (h / 2) - 10, w, 20, HorizontalAlignment.Center, VerticalAlignment.Center);

            // Medidas
            canvas.FontSize = 9;
            canvas.DrawString($"{realW:F2}m", x, y - 18, w, 15, HorizontalAlignment.Center, VerticalAlignment.Center);

            canvas.SaveState();
            canvas.Translate(x - 18, y + h / 2);
            canvas.Rotate(-90);
            canvas.DrawString($"{realH:F2}m", -h / 2, 0, h, 15, HorizontalAlignment.Center, VerticalAlignment.Center);
            canvas.RestoreState();

            // Acabamentos desprendidos (vista explodida)
            float offset = 18;
            float midX = x + w / 2;
            float midY = y + h / 2;

            // Rodobanca Trás
            if (rbT > LIMIAR_ACABAMENTO)
            {
                float yTop = y - offset;
                canvas.StrokeColor = CorRodobanca;
                canvas.StrokeSize = 4;
                canvas.DrawLine(x, yTop, x + w, yTop);

                // Linha tracejada de conexão
                canvas.StrokeColor = CorSeta;
                canvas.StrokeSize = 1;
                canvas.StrokeDashPattern = new float[] { 3, 3 };
                canvas.DrawLine(midX, y, midX, yTop);
                canvas.StrokeDashPattern = null;

                // Texto
                canvas.FontColor = CorRodobanca;
                canvas.FontSize = 8;
                canvas.DrawString($"RB {rbT:F2}m", x + 5, yTop - 3, 100, 12, HorizontalAlignment.Left, VerticalAlignment.Top);
            }

            // Saia Frente
            if (sF > LIMIAR_ACABAMENTO)
            {
                float yBottom = y + h + offset;
                canvas.StrokeColor = CorSaia;
                canvas.StrokeSize = 3.5f;
                canvas.DrawLine(x, yBottom, x + w, yBottom);

                // Linha tracejada de conexão
                canvas.StrokeColor = CorSeta;
                canvas.StrokeSize = 1;
                canvas.StrokeDashPattern = new float[] { 3, 3 };
                canvas.DrawLine(midX, y + h, midX, yBottom);
                canvas.StrokeDashPattern = null;

                // Texto
                canvas.FontColor = CorSaia;
                canvas.FontSize = 8;
                canvas.DrawString($"SAIA {sF:F2}m", x + 5, yBottom + 3, 100, 12, HorizontalAlignment.Left, VerticalAlignment.Top);
            }

            // Rodobanca Lateral Esquerda
            if (rbE > LIMIAR_ACABAMENTO && pecaId != "P3")
            {
                float xLeft = x - offset;
                canvas.StrokeColor = CorRodobanca;
                canvas.StrokeSize = 4;
                canvas.DrawLine(xLeft, y, xLeft, y + h);

                canvas.StrokeColor = CorSeta;
                canvas.StrokeSize = 1;
                canvas.StrokeDashPattern = new float[] { 3, 3 };
                canvas.DrawLine(x, midY, xLeft, midY);
                canvas.StrokeDashPattern = null;

                canvas.FontColor = CorRodobanca;
                canvas.FontSize = 8;
                canvas.DrawString($"RB {rbE:F2}m", xLeft - 35, midY - 5, 40, 12, HorizontalAlignment.Right, VerticalAlignment.Top);
            }

            // Rodobanca Lateral Direita
            if (rbD > LIMIAR_ACABAMENTO && pecaId != "P2")
            {
                float xRight = x + w + offset;
                canvas.StrokeColor = CorRodobanca;
                canvas.StrokeSize = 4;
                canvas.DrawLine(xRight, y, xRight, y + h);

                canvas.StrokeColor = CorSeta;
                canvas.StrokeSize = 1;
                canvas.StrokeDashPattern = new float[] { 3, 3 };
                canvas.DrawLine(x + w, midY, xRight, midY);
                canvas.StrokeDashPattern = null;

                canvas.FontColor = CorRodobanca;
                canvas.FontSize = 8;
                canvas.DrawString($"RB {rbD:F2}m", xRight + 5, midY - 5, 40, 12, HorizontalAlignment.Left, VerticalAlignment.Top);
            }

            // Recortes
            DesenharRecortes(canvas, x, y, escala, pecaId);
        }

        private void DesenharAcabamentoColado(IDrawingCanvas canvas, float x1, float y1, float x2, float y2, double valor, string pos)
        {
            if (valor <= LIMIAR_ACABAMENTO) return;

            canvas.StrokeColor = CorRodobanca;
            canvas.StrokeSize = 4;
            canvas.DrawLine(x1, y1, x2, y2);

            canvas.FontColor = CorRodobanca;
            canvas.FontSize = 8;

            // Posiciona o texto no INÍCIO da linha para não bater no centro
            switch (pos)
            {
                case "T": canvas.DrawString($"RB {valor:F2}m", x1 + 2, y1 - 12, 60, 10, HorizontalAlignment.Left, VerticalAlignment.Center); break;
                case "F": canvas.DrawString($"RB {valor:F2}m", x1 + 2, y1 + 4, 60, 10, HorizontalAlignment.Left, VerticalAlignment.Center); break;
                case "E": canvas.DrawString($"RB {valor:F2}m", x1 - 38, y1 + 5, 35, 10, HorizontalAlignment.Right, VerticalAlignment.Center); break;
                case "D": canvas.DrawString($"RB {valor:F2}m", x1 + 4, y1 + 5, 35, 10, HorizontalAlignment.Left, VerticalAlignment.Center); break;
            }
        }

        private void DesenharSaiaColada(IDrawingCanvas canvas, float x1, float y1, float x2, float y2, double valor, string pos)
        {
            if (valor <= LIMIAR_ACABAMENTO) return;

            canvas.StrokeColor = CorSaia;
            canvas.StrokeSize = 3.5f;
            canvas.DrawLine(x1, y1, x2, y2);

            canvas.FontColor = CorSaia;
            canvas.FontSize = 8;
            // Posiciona no FINAL da linha para evitar conflito com a medida central
            canvas.DrawString($"S {valor:F2}m", x2 - 42, y1 + 4, 40, 10, HorizontalAlignment.Right, VerticalAlignment.Center);
        }
        private void DesenharRecortes(IDrawingCanvas canvas, float xPeca, float yPeca, float escala, string pecaId)
        {

            canvas.StrokeDashPattern = null;
            // Bojo (Cuba)
            if (vm.TemBojo && vm.PecaDestinoBojo == pecaId)
            {
                float w = (float)(ConverterParaDouble(vm.LarguraBojoInput) * escala);
                float h = (float)(ConverterParaDouble(vm.AlturaBojoInput) * escala);
                float x = xPeca + (float)(ConverterParaDouble(vm.BojoXInput) * escala);
                float y = yPeca + (float)(ConverterParaDouble(vm.BojoYInput) * escala);

                canvas.StrokeColor = CorRecorteBojo;
                canvas.StrokeSize = 2;
                canvas.StrokeDashPattern = new float[] { 6, 3 };
                canvas.DrawRectangle(x, y, w, h);

                canvas.FontColor = CorRecorteBojo;
                canvas.FontSize = 9;
                canvas.DrawString("CUBA", x, y + (h / 2) - 10, w, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
            }

            // Cooktop
            if (vm.TemCooktop && vm.PecaDestinoCooktop == pecaId)
            {
                float w = (float)(ConverterParaDouble(vm.LarguraCooktopInput) * escala);
                float h = (float)(ConverterParaDouble(vm.AlturaCooktopInput) * escala);
                float x = xPeca + (float)(ConverterParaDouble(vm.CooktopXInput) * escala);
                float y = yPeca + (float)(ConverterParaDouble(vm.CooktopYInput) * escala);

                canvas.StrokeColor = CorRecorteCooktop;
                canvas.StrokeSize = 2;
                canvas.StrokeDashPattern = new float[] { 6, 3 };
                canvas.DrawRectangle(x, y, w, h);

                canvas.FontColor = CorRecorteCooktop;
                canvas.FontSize = 9;
                canvas.DrawString("COOKTOP", x, y + (h / 2) - 10, w, 20, HorizontalAlignment.Center, VerticalAlignment.Center);
                canvas.DrawString($"{ConverterParaDouble(vm.LarguraCooktopInput):N2}x{ConverterParaDouble(vm.AlturaCooktopInput):N2}",
                    x, y + h + 2, w, 15, HorizontalAlignment.Center, VerticalAlignment.Top);
                canvas.StrokeDashPattern = null;
            }
        }

        private void DesenharSetaConexao(IDrawingCanvas canvas, float x1, float y1, float x2, float y2)
            {
                canvas.StrokeColor = CorSeta;
                canvas.StrokeSize = 1;
                canvas.StrokeDashPattern = new float[] { 4, 4 };

                canvas.DrawLine(x1, y1, x2, y2);

                canvas.StrokeDashPattern = null;

                float tamanho = 6;

                // seta direita
                canvas.DrawLine(x2 - tamanho, y2 - tamanho, x2, y2);
                canvas.DrawLine(x2 - tamanho, y2 + tamanho, x2, y2);

                // seta esquerda
                canvas.DrawLine(x1 + tamanho, y1 - tamanho, x1, y1);
                canvas.DrawLine(x1 + tamanho, y1 + tamanho, x1, y1);
            }

        private double ConverterParaDouble(string valor)
        {
            if (string.IsNullOrWhiteSpace(valor))
                return 0;

            valor = valor.Replace(',', '.');

            if (double.TryParse(
                valor,
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture,
                out double resultado))
            {
                return resultado;
            }

            return 0;
        }
    }
}