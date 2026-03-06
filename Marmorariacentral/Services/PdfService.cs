using SkiaSharp;
using Microsoft.Maui.Storage;
using Microsoft.Maui.Controls;
using System.Diagnostics;
using Marmorariacentral.Models;
using System.Globalization;
using Microsoft.Maui.ApplicationModel.DataTransfer;

namespace Marmorariacentral.Services;

public class PdfService
{
    private readonly SKTypeface _fonteNormal = SKTypeface.FromFamilyName("Arial", SKFontStyleWeight.Normal, SKFontStyleWidth.Normal, SKFontStyleSlant.Upright);
    private readonly SKTypeface _fonteBold = SKTypeface.FromFamilyName("Arial", SKFontStyleWeight.Bold, SKFontStyleWidth.Normal, SKFontStyleSlant.Upright);

    // Identidade Visual do App
    private readonly SKColor CorPrimaria = SKColor.Parse("#8B1A1A"); // Vermelho Bordô do App
    private readonly SKColor CorTextoEscuro = SKColor.Parse("#212121");
    private readonly SKColor CorTextoCinza = SKColor.Parse("#757575");
    private readonly SKColor CorFundoDesenho = SKColor.Parse("#F9F9F9");

    // Cores técnicas para o desenho
    private readonly SKColor CorPeca = SKColors.LightGray;
    private readonly SKColor CorRodobanca = SKColor.Parse("#2E7D32"); // Verde
    private readonly SKColor CorSaia = SKColor.Parse("#B76E00");      // Amarelo/Ouro
    private readonly SKColor CorSeta = SKColor.Parse("#555555");

    public async Task GerarPdfTecnicoAsync(Cliente cliente, List<PecaOrcamento> pecas, View? viewParaCapturar = null)
    {
        await GerarDocumentoConsolidado(cliente, pecas, isTecnico: true);
    }

    public async Task GerarPdfClienteAsync(Cliente cliente, List<PecaOrcamento> pecas, View? viewParaCapturar = null)
    {
        await GerarDocumentoConsolidado(cliente, pecas, isTecnico: false);
    }

    private async Task GerarDocumentoConsolidado(Cliente cliente, List<PecaOrcamento> pecas, bool isTecnico)
    {
        if (cliente == null || pecas == null || !pecas.Any()) return;

        try
        {
            string prefixo = isTecnico ? "GuiaTecnica" : "Orcamento";
            var caminhoPdf = Path.Combine(FileSystem.CacheDirectory, $"{prefixo}_{cliente.Nome.Replace(" ", "_")}.pdf");

            using (var streamPdf = File.OpenWrite(caminhoPdf))
            using (var document = SKDocument.CreatePdf(streamPdf))
            {
                float larguraPagina = 595; // A4
                float alturaPagina = 842;
                float margem = 40;

                var canvas = document.BeginPage(larguraPagina, alturaPagina);
                float yAtual = margem;

                using (var paint = new SKPaint { IsAntialias = true })
                {
                    // --- CABEÇALHO ---
                    paint.Color = CorPrimaria;
                    canvas.DrawRect(0, 0, 10, alturaPagina, paint);

                    paint.Typeface = _fonteBold;
                    paint.TextSize = 24;
                    paint.Color = CorPrimaria;
                    canvas.DrawText("CENTRAL GRANITOS", margem, yAtual + 25, paint);

                    paint.Typeface = _fonteNormal;
                    paint.TextSize = 9;
                    paint.Color = CorTextoCinza;
                    float xDados = larguraPagina - margem - 180;
                    canvas.DrawText("Praça Pres. Getúlio Vargas, 129 - Centro", xDados, yAtual + 10, paint);
                    canvas.DrawText("Carmo do Cajuru - MG", xDados, yAtual + 22, paint);
                    canvas.DrawText("Tel: (37) 98407-2955 / 98412-7829", xDados, yAtual + 34, paint);
                    canvas.DrawText("Instagram: @central_granitos", xDados, yAtual + 46, paint);

                    yAtual += 65;
                    
                    paint.Color = isTecnico ? SKColors.DarkSlateGray : CorPrimaria;
                    paint.TextSize = 16;
                    paint.Typeface = _fonteBold;
                    string titulo = isTecnico ? "GUIA TÉCNICA DE PRODUÇÃO" : "ORÇAMENTO DE MARMORARIA";
                    canvas.DrawText(titulo, margem, yAtual, paint);

                    yAtual += 10;
                    canvas.DrawLine(margem, yAtual, larguraPagina - margem, yAtual, new SKPaint { Color = CorPrimaria, StrokeWidth = 2 });

                    yAtual += 25;
                    paint.TextSize = 11;
                    paint.Color = CorTextoEscuro;
                    canvas.DrawText($"CLIENTE: {cliente.Nome.ToUpper()}", margem, yAtual, paint);
                    yAtual += 15;
                    canvas.DrawText($"ENDEREÇO: {cliente.Endereco ?? "Não informado"}", margem, yAtual, paint);
                    
                    yAtual += 30;

                    double totalFinanceiro = 0;

                    foreach (var peca in pecas)
                    {
                        if (yAtual > 650)
                        {
                            document.EndPage();
                            canvas = document.BeginPage(larguraPagina, alturaPagina);
                            yAtual = margem + 20;
                            paint.Color = CorPrimaria;
                            canvas.DrawRect(0, 0, 10, alturaPagina, paint);
                        }

                        paint.Typeface = _fonteBold;
                        paint.TextSize = 13;
                        paint.Color = CorPrimaria;
                        canvas.DrawText($"{peca.Ambiente.ToUpper()} - {peca.PedraNome} (x{peca.Quantidade})", margem, yAtual, paint);
                        
                        yAtual += 15;

                        float alturaQuadro = 220;
                        SKRect rectQuadro = new SKRect(margem, yAtual, larguraPagina - margem, yAtual + alturaQuadro);
                        paint.Style = SKPaintStyle.Fill;
                        paint.Color = CorFundoDesenho;
                        canvas.DrawRoundRect(rectQuadro, 10, 10, paint);
                        
                        DesenharPecaTecnicaNoPdf(canvas, rectQuadro, peca);
                        
                        yAtual += alturaQuadro + 20;

                        if (isTecnico)
                        {
                            paint.Typeface = _fonteNormal;
                            paint.Color = CorTextoEscuro;
                            paint.TextSize = 10;
                            string detalhes = $"MEDIDAS PRODUÇÃO: P1 ({peca.Largura:N2}x{peca.Altura:N2})";
                            if (peca.LarguraP2 > 0) detalhes += $" | P2 ({peca.LarguraP2:N2}x{peca.AlturaP2:N2})";
                            canvas.DrawText(detalhes, margem + 10, yAtual, paint);
                        }
                        else
                        {
                            paint.Typeface = _fonteBold;
                            paint.Color = CorPrimaria;
                            paint.TextSize = 12;
                            string valorPeca = $"Subtotal da Peça: {peca.ValorTotalPeca:C}";
                            canvas.DrawText(valorPeca, larguraPagina - margem - paint.MeasureText(valorPeca) - 10, yAtual, paint);
                            totalFinanceiro += peca.ValorTotalPeca;
                        }

                        yAtual += 40;
                    }

                    if (!isTecnico)
                    {
                        paint.Color = CorPrimaria;
                        canvas.DrawRect(margem, alturaPagina - 80, larguraPagina - (margem * 2), 40, paint);
                        
                        paint.Color = SKColors.White;
                        paint.TextSize = 16;
                        string totalTxt = $"TOTAL GERAL DO ORÇAMENTO: {totalFinanceiro:C}";
                        canvas.DrawText(totalTxt, larguraPagina / 2 - (paint.MeasureText(totalTxt) / 2), alturaPagina - 55, paint);
                    }

                    document.EndPage();
                }
                document.Close();
            }

            // CORREÇÃO DO ERRO CS1503: Usando a requisição correta do MAUI
            await Share.Default.RequestAsync(new ShareFileRequest
            {
                Title = prefixo,
                File = new ShareFile(caminhoPdf)
            });
        }
        catch (Exception ex) { Debug.WriteLine($"Erro ao gerar PDF: {ex.Message}"); }
    }

    private void DesenharPecaTecnicaNoPdf(SKCanvas canvas, SKRect rect, PecaOrcamento p)
    {
        float espacoExplodido = 30;
        double largEsq = (p.LadoP2 == "Esquerda") ? p.LarguraP2 : 0;
        double largDir = (p.LadoP2 == "Direita") ? p.LarguraP2 : (p.LarguraP3 > 0 ? p.LarguraP3 : 0);
        
        float totalEspacos = 0;
        if (largEsq > 0) totalEspacos += espacoExplodido;
        if (largDir > 0) totalEspacos += espacoExplodido;

        double largTot = p.Largura + largEsq + largDir;
        double altMax = Math.Max(p.Altura, Math.Max(p.AlturaP2, p.AlturaP3));

        float escala = (float)Math.Min((rect.Width - 80 - totalEspacos) / largTot, (rect.Height - 80) / altMax);
        
        float xPeca = rect.Left + (rect.Width - (float)(largTot * escala) - totalEspacos) / 2;
        float yPeca = rect.Top + (rect.Height - (float)(altMax * escala)) / 2;

        using (var paint = new SKPaint { IsAntialias = true, StrokeWidth = 1.5f })
        {
            if (p.LadoP2 == "Esquerda" && p.LarguraP2 > 0)
            {
                DesenharBloco(canvas, xPeca, yPeca, (float)(p.LarguraP2 * escala), (float)(p.AlturaP2 * escala), "P2", $"{p.LarguraP2:N2}m", paint);
                DesenharSeta(canvas, xPeca + (float)(p.LarguraP2 * escala), yPeca + 20, xPeca + (float)(p.LarguraP2 * escala) + espacoExplodido, yPeca + 20, paint);
                xPeca += (float)(p.LarguraP2 * escala) + espacoExplodido;
            }

            DesenharBloco(canvas, xPeca, yPeca, (float)(p.Largura * escala), (float)(p.Altura * escala), "P1", $"{p.Largura:N2}m", paint);
            
            if (p.RodobancaP1Tras > 0) { paint.Color = CorRodobanca; paint.StrokeWidth = 4; canvas.DrawLine(xPeca, yPeca, xPeca + (float)(p.Largura * escala), yPeca, paint); }
            if (p.SaiaP1Frente > 0) { paint.Color = CorSaia; paint.StrokeWidth = 4; canvas.DrawLine(xPeca, yPeca + (float)(p.Altura * escala), xPeca + (float)(p.Largura * escala), yPeca + (float)(p.Altura * escala), paint); }

            if (largDir > 0)
            {
                float xFimP1 = xPeca + (float)(p.Largura * escala);
                DesenharSeta(canvas, xFimP1, yPeca + 20, xFimP1 + espacoExplodido, yPeca + 20, paint);
                
                float xDir = xFimP1 + espacoExplodido;
                double lD = (p.LadoP2 == "Direita") ? p.LarguraP2 : p.LarguraP3;
                double aD = (p.LadoP2 == "Direita") ? p.AlturaP2 : p.AlturaP3;
                DesenharBloco(canvas, xDir, yPeca, (float)(lD * escala), (float)(aD * escala), "P2", $"{lD:N2}m", paint);
            }
        }
    }

    private void DesenharBloco(SKCanvas canvas, float x, float y, float w, float h, string label, string medida, SKPaint paint)
    {
        paint.Style = SKPaintStyle.Fill;
        paint.Color = SKColors.WhiteSmoke;
        canvas.DrawRect(x, y, w, h, paint);

        paint.Style = SKPaintStyle.Stroke;
        paint.Color = SKColors.Black;
        paint.StrokeWidth = 1;
        canvas.DrawRect(x, y, w, h, paint);

        paint.Style = SKPaintStyle.Fill;
        paint.Typeface = _fonteBold;
        paint.TextSize = 10;
        canvas.DrawText(label, x + (w/2) - 6, y + (h/2) + 4, paint);
        
        paint.Typeface = _fonteNormal;
        paint.TextSize = 8;
        canvas.DrawText(medida, x + (w/2) - 12, y - 5, paint);
    }

    private void DesenharSeta(SKCanvas canvas, float x1, float y1, float x2, float y2, SKPaint paint)
    {
        paint.Color = CorSeta;
        paint.StrokeWidth = 1;
        paint.PathEffect = SKPathEffect.CreateDash(new float[] { 3, 3 }, 0);
        canvas.DrawLine(x1, y1, x2, y2, paint);
        paint.PathEffect = null;
        canvas.DrawCircle(x1, y1, 2, paint);
        canvas.DrawCircle(x2, y2, 2, paint);
    }

    // MÉTODOS DE COMPATIBILIDADE PARA A CALCULADORA
    public async Task GerarDocumentoTecnico(View v, string c, string p, int q) 
    {
        var clienteFake = new Cliente { Nome = c };
        var pecaFake = new List<PecaOrcamento> { new PecaOrcamento { PedraNome = p, Quantidade = q, Ambiente = "Peça Única" } };
        await GerarPdfTecnicoAsync(clienteFake, pecaFake, v);
    }

    public async Task GerarOrcamentoCliente(View v, string c, string p, int q, double t) 
    {
        var clienteFake = new Cliente { Nome = c };
        var pecaFake = new List<PecaOrcamento> { new PecaOrcamento { PedraNome = p, Quantidade = q, ValorTotalPeca = t, Ambiente = "Peça Única" } };
        await GerarPdfClienteAsync(clienteFake, pecaFake, v);
    }
}