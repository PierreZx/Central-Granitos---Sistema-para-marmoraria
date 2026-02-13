using Marmorariacentral.ViewModels;
using Microsoft.Maui.Graphics;

public class PecaDrawable : IDrawable
{
    private readonly CalculadoraPecaViewModel vm;
    private const float MARGEM_INTERNA = 60;
    private const float TAMANHO_MAXIMO_PECA = 400;

    public PecaDrawable(CalculadoraPecaViewModel viewModel)
    {
        vm = viewModel;
    }

    public void Draw(ICanvas canvas, RectF dirtyRect)
    {
        try
        {
            canvas.Antialias = true;
            canvas.FillColor = Colors.White;
            canvas.FillRectangle(dirtyRect);

            double larguraBase = vm.Peca.Largura;
            double alturaBase = vm.Peca.Altura;

            if (larguraBase <= 0.01 || alturaBase <= 0.01)
            {
                DesenharMensagemSemPeca(canvas, dirtyRect);
                return;
            }

            // ====================================================================
            // DEFINIÇÃO DAS PEÇAS - SEM PROPRIEDADES TemBancadaL/TemBancadaU
            // ====================================================================
            
            double larguraEsquerda = 0;
            double alturaEsquerda = 0;
            double larguraDireita = 0;
            double alturaDireita = 0;
            
            bool temPernaEsquerda = false;
            bool temPernaDireita = false;

            // ========================================
            // BANCADA EM L - SÓ EXISTE SE TIVER MEDIDAS
            // ========================================
            if (vm.Peca2.Largura > 0.01 && vm.Peca2.Altura > 0.01)
            {
                if (vm.LadoP2 == "Esquerda")
                {
                    larguraEsquerda = vm.Peca2.Largura;
                    alturaEsquerda = vm.Peca2.Altura;
                    temPernaEsquerda = true;
                }
                else
                {
                    larguraDireita = vm.Peca2.Largura;
                    alturaDireita = vm.Peca2.Altura;
                    temPernaDireita = true;
                }
            }

            // ========================================
            // BANCADA EM U - SÓ EXISTE SE TIVER MEDIDAS
            // ========================================
            if (vm.Peca3.Largura > 0.01 && vm.Peca3.Altura > 0.01)
            {
                // Se já tem perna esquerda do L, adiciona direita
                if (temPernaEsquerda)
                {
                    larguraDireita = vm.Peca3.Largura;
                    alturaDireita = vm.Peca3.Altura;
                    temPernaDireita = true;
                }
                // Se já tem perna direita do L, adiciona esquerda
                else if (temPernaDireita)
                {
                    larguraEsquerda = vm.Peca3.Largura;
                    alturaEsquerda = vm.Peca3.Altura;
                    temPernaEsquerda = true;
                }
                // Se não tem nenhuma perna, adiciona as DUAS
                else
                {
                    larguraEsquerda = vm.Peca3.Largura;
                    alturaEsquerda = vm.Peca3.Altura;
                    larguraDireita = vm.Peca3.Largura;
                    alturaDireita = vm.Peca3.Altura;
                    temPernaEsquerda = true;
                    temPernaDireita = true;
                }
            }

            // ====================================================================
            // CÁLCULO DE ESCALA
            // ====================================================================
            
            double larguraTotal = larguraBase + larguraEsquerda + larguraDireita;
            double alturaMaxima = Math.Max(alturaBase, Math.Max(alturaEsquerda, alturaDireita));

            float areaUtilW = dirtyRect.Width - MARGEM_INTERNA * 2;
            float areaUtilH = dirtyRect.Height - MARGEM_INTERNA * 2;

            float escala = Math.Min(
                areaUtilW / (float)larguraTotal,
                areaUtilH / (float)alturaMaxima
            );

            float escalaMaxima = TAMANHO_MAXIMO_PECA / (float)Math.Max(larguraBase, alturaBase);
            escala = Math.Min(escala, escalaMaxima);
            
            if (float.IsNaN(escala) || float.IsInfinity(escala) || escala <= 0)
                escala = 1;

            // ====================================================================
            // POSICIONAMENTO - ALINHADO PELO TOPO
            // ====================================================================
            
            float larguraTotalPx = (float)(larguraTotal * escala);
            float alturaMaximaPx = (float)(alturaMaxima * escala);

            float centroX = dirtyRect.Width / 2;
            float centroY = dirtyRect.Height / 2;

            float xInicial = centroX - (larguraTotalPx / 2);
            float yInicial = MARGEM_INTERNA;

            float larguraPrincipalPx = (float)(larguraBase * escala);
            float alturaPrincipalPx = (float)(alturaBase * escala);
            
            float larguraEsquerdaPx = (float)(larguraEsquerda * escala);
            float alturaEsquerdaPx = (float)(alturaEsquerda * escala);
            
            float larguraDireitaPx = (float)(larguraDireita * escala);
            float alturaDireitaPx = (float)(alturaDireita * escala);

            float xPrincipal = xInicial + larguraEsquerdaPx;
            
            float yPrincipal = yInicial;
            float yEsquerda = yInicial;
            float yDireita = yInicial;

            // ====================================================================
            // DESENHO DAS PEÇAS
            // ====================================================================

            // PERNA ESQUERDA
            if (temPernaEsquerda && larguraEsquerdaPx > 1 && alturaEsquerdaPx > 1)
            {
                DesenharPeca(canvas, 
                    xPrincipal - larguraEsquerdaPx, 
                    yEsquerda, 
                    larguraEsquerdaPx, 
                    alturaEsquerdaPx, 
                    "#A5D8FF");
            }

            // PEÇA PRINCIPAL
            DesenharPeca(canvas, 
                xPrincipal, 
                yPrincipal, 
                larguraPrincipalPx, 
                alturaPrincipalPx, 
                "#E8E8E8");

            // PERNA DIREITA
            if (temPernaDireita && larguraDireitaPx > 1 && alturaDireitaPx > 1)
            {
                DesenharPeca(canvas, 
                    xPrincipal + larguraPrincipalPx, 
                    yDireita, 
                    larguraDireitaPx, 
                    alturaDireitaPx, 
                    "#A5D8FF");
            }

            // ====================================================================
            // DESENHO DAS MEDIDAS
            // ====================================================================

            canvas.FontSize = 13;
            canvas.FontColor = Colors.Black;

            // Largura Principal
            if (larguraPrincipalPx > 30)
            {
                canvas.DrawString($"{vm.Peca.Largura:F2} m",
                    xPrincipal, 
                    yPrincipal + alturaPrincipalPx + 5,
                    larguraPrincipalPx, 
                    22,
                    HorizontalAlignment.Center, 
                    VerticalAlignment.Top);
            }

            // Altura Principal
            if (alturaPrincipalPx > 30)
            {
                canvas.SaveState();
                canvas.Rotate(-90, xPrincipal - 35, yPrincipal + alturaPrincipalPx / 2);
                canvas.DrawString($"{vm.Peca.Altura:F2} m",
                    xPrincipal - 45, 
                    yPrincipal + alturaPrincipalPx / 2 - 8,
                    30, 
                    alturaPrincipalPx,
                    HorizontalAlignment.Center, 
                    VerticalAlignment.Center);
                canvas.RestoreState();
            }

            // Perna Esquerda
            if (temPernaEsquerda && larguraEsquerdaPx > 30 && alturaEsquerdaPx > 30)
            {
                canvas.DrawString($"{larguraEsquerda:F2} m",
                    xPrincipal - larguraEsquerdaPx, 
                    yPrincipal + alturaPrincipalPx + 5,
                    larguraEsquerdaPx, 
                    22,
                    HorizontalAlignment.Center, 
                    VerticalAlignment.Top);
                
                canvas.SaveState();
                canvas.Rotate(-90, 
                    xPrincipal - larguraEsquerdaPx - 35, 
                    yEsquerda + alturaEsquerdaPx / 2);
                canvas.DrawString($"{alturaEsquerda:F2} m",
                    xPrincipal - larguraEsquerdaPx - 45, 
                    yEsquerda + alturaEsquerdaPx / 2 - 8,
                    30, 
                    alturaEsquerdaPx,
                    HorizontalAlignment.Center, 
                    VerticalAlignment.Center);
                canvas.RestoreState();
            }

            // Perna Direita
            if (temPernaDireita && larguraDireitaPx > 30 && alturaDireitaPx > 30)
            {
                canvas.DrawString($"{larguraDireita:F2} m",
                    xPrincipal + larguraPrincipalPx, 
                    yPrincipal + alturaPrincipalPx + 5,
                    larguraDireitaPx, 
                    22,
                    HorizontalAlignment.Center, 
                    VerticalAlignment.Top);
                
                canvas.SaveState();
                canvas.Rotate(-90, 
                    xPrincipal + larguraPrincipalPx + larguraDireitaPx + 35, 
                    yDireita + alturaDireitaPx / 2);
                canvas.DrawString($"{alturaDireita:F2} m",
                    xPrincipal + larguraPrincipalPx + larguraDireitaPx + 25, 
                    yDireita + alturaDireitaPx / 2 - 8,
                    30, 
                    alturaDireitaPx,
                    HorizontalAlignment.Center, 
                    VerticalAlignment.Center);
                canvas.RestoreState();
            }

            // ====================================================================
            // LEGENDA
            // ====================================================================
            
            canvas.FontSize = 11;
            canvas.FontColor = Colors.Gray;
            
            string legenda = "⬜ Principal";
            if (temPernaEsquerda) legenda += "   🟦 Perna Esq";
            if (temPernaDireita) legenda += "   🟦 Perna Dir";
            
            canvas.DrawString(legenda,
                dirtyRect.Width / 2, 
                dirtyRect.Height - 20,
                500, 
                18,
                HorizontalAlignment.Center, 
                VerticalAlignment.Bottom);
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Erro no desenho: {ex.Message}");
        }
    }

    private void DesenharPeca(ICanvas canvas, float x, float y, float w, float h, string corHex)
    {
        if (w <= 1 || h <= 1) return;

        canvas.FillColor = Color.FromArgb(corHex);
        canvas.FillRectangle(x, y, w, h);

        canvas.StrokeColor = Colors.Black;
        canvas.StrokeSize = 1.8f;
        canvas.DrawRectangle(x, y, w, h);

        canvas.StrokeColor = Color.FromArgb("#999999");
        canvas.StrokeSize = 0.6f;
        canvas.StrokeDashPattern = new float[] { 2, 3 };
        canvas.DrawLine(x + 4, y + 4, x + w - 4, y + h - 4);
        canvas.StrokeDashPattern = null;
    }

    private void DesenharMensagemSemPeca(ICanvas canvas, RectF dirtyRect)
    {
        canvas.FontSize = 18;
        canvas.FontColor = Colors.Gray;
        
        canvas.DrawString("🪨 Desenho da peça",
            dirtyRect.Width / 2, 
            dirtyRect.Height / 2 - 25,
            300, 
            30,
            HorizontalAlignment.Center, 
            VerticalAlignment.Center);
        
        canvas.FontSize = 14;
        canvas.FontColor = Colors.LightGray;
        canvas.DrawString("Preencha as medidas",
            dirtyRect.Width / 2, 
            dirtyRect.Height / 2 + 15,
            300, 
            25,
            HorizontalAlignment.Center, 
            VerticalAlignment.Center);
    }
}