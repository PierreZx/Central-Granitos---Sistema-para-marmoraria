using SkiaSharp;
using Microsoft.Maui.Storage;
using Microsoft.Maui.Controls;
using System.Diagnostics;
using Marmorariacentral.Models;
using System.Globalization;
using System.Text;
using Microsoft.Maui.ApplicationModel.DataTransfer;
using Marmorariacentral.Drawables;
using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Services;

public class PdfService
{
    private readonly SKTypeface _fonteNormal = SKTypeface.FromFamilyName("Arial", SKFontStyleWeight.Normal, SKFontStyleWidth.Normal, SKFontStyleSlant.Upright);
    private readonly SKTypeface _fonteBold = SKTypeface.FromFamilyName("Arial", SKFontStyleWeight.Bold, SKFontStyleWidth.Normal, SKFontStyleSlant.Upright);

    // Identidade Visual do App
    private readonly SKColor CorPrimaria = SKColor.Parse("#8B1A1A"); // Vermelho Bordô Central
    private readonly SKColor CorTextoEscuro = SKColor.Parse("#212121");
    private readonly SKColor CorTextoCinza = SKColor.Parse("#757575");
    private readonly SKColor CorFundoDesenho = SKColor.Parse("#F9F9F9");
    
    // Cores técnicas para o desenho
    private readonly SKColor CorPeca = SKColors.LightGray;
    private readonly SKColor CorRodobanca = SKColor.Parse("#2E7D32"); // Verde
    private readonly SKColor CorSaia = SKColor.Parse("#B76E00");      // Amarelo/Ouro
    private readonly SKColor CorSetaGuia = SKColor.Parse("#888888");
    private readonly SKColor CorTextoMedidas = SKColor.Parse("#333333");
    private readonly SKColor CorLinhaCota = SKColor.Parse("#666666");

    /// <summary>
    /// Gera a Guia Técnica de Produção (Vista Explodida)
    /// </summary>
    public async Task GerarPdfTecnicoAsync(Cliente cliente, List<PecaOrcamento> pecas, View? viewParaCapturar = null)
    {
        await GerarDocumentoConsolidado(cliente, pecas, isTecnico: true);
    }

    /// <summary>
    /// Gera o Orçamento Comercial para o Cliente (Vista Estética)
    /// </summary>
    public async Task GerarPdfClienteAsync(Cliente cliente, List<PecaOrcamento> pecas, View? viewParaCapturar = null)
    {
        await GerarDocumentoConsolidado(cliente, pecas, isTecnico: false);
    }

    private string SanitizarNomeArquivo(string nome)
    {
        if (string.IsNullOrEmpty(nome)) return "SemNome";
        
        var nomeSanitizado = nome;
        foreach (char c in Path.GetInvalidFileNameChars())
        {
            nomeSanitizado = nomeSanitizado.Replace(c, '_');
        }
        return nomeSanitizado.Replace(" ", "_");
    }

    private void AdicionarListaProdução(SKCanvas canvas, SKPaint paint, PecaOrcamento peca, float x, float y)
    {
        paint.Typeface = _fonteBold;
        paint.TextSize = 9;
        paint.Color = CorTextoEscuro;
        
        float yLista = y;
        
        canvas.DrawText("LISTA DE CORTE:", x, yLista, paint);
        yLista += 12;
        
        paint.Typeface = _fonteNormal;
        paint.TextSize = 8;
        
        canvas.DrawText($"P1: {peca.Largura:F2} x {peca.Altura:F2}", x, yLista, paint);
        yLista += 10;
        
        if (peca.LarguraP2 > 0.01)
        {
            string lado = string.IsNullOrEmpty(peca.LadoP2) ? "" : $" ({peca.LadoP2})";
            canvas.DrawText($"P2{lado}: {peca.LarguraP2:F2} x {peca.AlturaP2:F2}", x, yLista, paint);
            yLista += 10;
        }
        
        if (peca.LarguraP3 > 0.01)
        {
            string lado = string.IsNullOrEmpty(peca.LadoP3) ? "" : $" ({peca.LadoP3})";
            canvas.DrawText($"P3{lado}: {peca.LarguraP3:F2} x {peca.AlturaP3:F2}", x, yLista, paint);
            yLista += 10;
        }
        
        // Acabamentos
        bool temAcabamento = false;
        string acabamentos = "";
        
        if (peca.RodobancaP1Tras > 0.01 || peca.RodobancaP1Esquerda > 0.01 || 
            peca.RodobancaP1Direita > 0.01 || peca.RodobancaP1Frente > 0.01 ||
            peca.RodobancaP2Tras > 0.01 || peca.RodobancaP3Tras > 0.01)
        {
            acabamentos += "RB ";
            temAcabamento = true;
        }
        
        if (peca.SaiaP1Frente > 0.01 || peca.SaiaP2Frente > 0.01 || peca.SaiaP3Frente > 0.01)
        {
            acabamentos += "SAIA ";
            temAcabamento = true;
        }
        
        if (peca.TemBojo) acabamentos += "CUBA ";
        if (peca.TemCooktop) acabamentos += "COOKTOP ";
        
        if (temAcabamento)
        {
            canvas.DrawText($"Acab.: {acabamentos}", x, yLista, paint);
        }
    }

    private SKBitmap DesenharPecaEmBitmap(PecaOrcamento peca, bool isTecnico, int largura, int altura)
    {
        var bitmap = new SKBitmap(largura, altura);

        using var canvas = new SKCanvas(bitmap);

        // Limpa o fundo para garantir que o desenho comece sobre branco
        canvas.Clear(SKColors.White);

        // Cria uma ViewModel temporária para alimentar o PecaDrawable
        var vmTemp = new CalculadoraPecaViewModel(null, null);

        // Mapeamento dos dados principais
        vmTemp.Peca = peca;
        vmTemp.LadoP2 = peca.LadoP2 ?? "Esquerda";
        vmTemp.LadoP3 = peca.LadoP3 ?? "Direita";

        // Mapeamento completo de Rodobancas (P1, P2 e P3)
        vmTemp.RodobancaP1Esquerda = peca.RodobancaP1Esquerda;
        vmTemp.RodobancaP1Direita = peca.RodobancaP1Direita;
        vmTemp.RodobancaP1Frente = peca.RodobancaP1Frente;
        vmTemp.RodobancaP1Tras = peca.RodobancaP1Tras;

        vmTemp.RodobancaP2Esquerda = peca.RodobancaP2Esquerda;
        vmTemp.RodobancaP2Direita = peca.RodobancaP2Direita;
        vmTemp.RodobancaP2Frente = peca.RodobancaP2Frente;
        vmTemp.RodobancaP2Tras = peca.RodobancaP2Tras;

        vmTemp.RodobancaP3Esquerda = peca.RodobancaP3Esquerda;
        vmTemp.RodobancaP3Direita = peca.RodobancaP3Direita;
        vmTemp.RodobancaP3Frente = peca.RodobancaP3Frente;
        vmTemp.RodobancaP3Tras = peca.RodobancaP3Tras;

        // Mapeamento completo de Saias
        vmTemp.SaiaP1Esquerda = peca.SaiaP1Esquerda;
        vmTemp.SaiaP1Direita = peca.SaiaP1Direita;
        vmTemp.SaiaP1Frente = peca.SaiaP1Frente;
        vmTemp.SaiaP1Tras = peca.SaiaP1Tras;

        vmTemp.SaiaP2Esquerda = peca.SaiaP2Esquerda;
        vmTemp.SaiaP2Direita = peca.SaiaP2Direita;
        vmTemp.SaiaP2Frente = peca.SaiaP2Frente;
        vmTemp.SaiaP2Tras = peca.SaiaP2Tras;

        vmTemp.SaiaP3Esquerda = peca.SaiaP3Esquerda;
        vmTemp.SaiaP3Direita = peca.SaiaP3Direita;
        vmTemp.SaiaP3Frente = peca.SaiaP3Frente;
        vmTemp.SaiaP3Tras = peca.SaiaP3Tras;

        // Mapeamento de Recortes (Cuba/Bojo)
        vmTemp.TemBojo = peca.TemBojo;
        vmTemp.PecaDestinoBojo = peca.PecaDestinoBojo ?? "P1";
        vmTemp.LarguraBojoInput = peca.LarguraBojo.ToString(CultureInfo.InvariantCulture);
        vmTemp.AlturaBojoInput = peca.AlturaBojo.ToString(CultureInfo.InvariantCulture);
        vmTemp.BojoXInput = peca.BojoX.ToString(CultureInfo.InvariantCulture);

        // Mapeamento de Recortes (Cooktop)
        vmTemp.TemCooktop = peca.TemCooktop;
        vmTemp.PecaDestinoCooktop = peca.PecaDestinoCooktop ?? "P1";
        vmTemp.LarguraCooktopInput = peca.LarguraCooktop.ToString(CultureInfo.InvariantCulture);
        vmTemp.AlturaCooktopInput = peca.AlturaCooktop.ToString(CultureInfo.InvariantCulture);
        vmTemp.CooktopXInput = peca.CooktopX.ToString(CultureInfo.InvariantCulture);

        // Instancia o Drawable com a configuração de vista técnica ou comercial
        var drawable = new PecaDrawable(vmTemp);
        drawable.IsVistaExplodida = isTecnico;

        // Utiliza o adaptador de Skia para realizar o desenho no canvas do bitmap
        var adapter = new SkiaCanvasAdapter(canvas);

        // Renderiza o desenho na área total do bitmap
        drawable.Draw(adapter, new RectF(0, 0, largura, altura));

        return bitmap;
    }

    private async Task GerarDocumentoConsolidado(Cliente cliente, List<PecaOrcamento> pecas, bool isTecnico)
    {
        if (cliente == null || pecas == null || !pecas.Any()) return;

        try
        {
            string prefixo = isTecnico ? "GuiaTecnica" : "Orcamento";
            var nomeClienteSanitizado = SanitizarNomeArquivo(cliente.Nome ?? "Cliente");
            var caminhoPdf = Path.Combine(FileSystem.CacheDirectory, $"{prefixo}_{nomeClienteSanitizado}.pdf");

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
                    // --- BARRA LATERAL ESTÉTICA ---
                    paint.Color = CorPrimaria;
                    canvas.DrawRect(0, 0, 10, alturaPagina, paint);

                    // --- CARREGAMENTO DA LOGO (Pasta Resources/Raw) ---
                    try 
                    {
                        using var streamLogo = await FileSystem.OpenAppPackageFileAsync("logo_central.png");
                        using var bitmapLogo = SKBitmap.Decode(streamLogo);
                        if (bitmapLogo != null)
                        {
                            float alturaLogo = 50;
                            float larguraLogo = (bitmapLogo.Width * alturaLogo) / bitmapLogo.Height;
                            canvas.DrawBitmap(bitmapLogo, new SKRect(margem, yAtual, margem + larguraLogo, yAtual + alturaLogo));
                        }
                    }
                    catch (Exception ex) { Debug.WriteLine($"Erro ao carregar logo: {ex.Message}"); }

                    // --- CABEÇALHO DA EMPRESA ---
                    paint.Typeface = _fonteBold;
                    paint.TextSize = 22;
                    paint.Color = CorPrimaria;
                    canvas.DrawText("CENTRAL GRANITOS", margem + 60, yAtual + 35, paint);

                    paint.Typeface = _fonteNormal;
                    paint.TextSize = 9;
                    paint.Color = CorTextoCinza;
                    float xDados = larguraPagina - margem - 180;
                    canvas.DrawText("Praça Pres. Getúlio Vargas, 129 - Centro", xDados, yAtual + 10, paint);
                    canvas.DrawText("Carmo do Cajuru - MG | (37) 98407-2955", xDados, yAtual + 22, paint);
                    canvas.DrawText("Instagram: @central_granitos", xDados, yAtual + 34, paint);

                    yAtual += 75;
                    
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
                    canvas.DrawText($"CLIENTE: {(cliente.Nome ?? "NÃO INFORMADO").ToUpper()}", margem, yAtual, paint);
                    yAtual += 15;
                    canvas.DrawText($"ENDEREÇO: {cliente.Endereco ?? "Não informado"}", margem, yAtual, paint);
                    
                    yAtual += 30;

                    double totalFinanceiro = 0;

                    foreach (var peca in pecas)
                    {
                        // Define a altura do quadro e o espaço total que a peça ocupa
                        float alturaQuadro = isTecnico ? 340 : 280; 
                        float espacoNecessario = alturaQuadro + 110; 

                        // CONTROLE DE NOVA PÁGINA: Se não couber a peça atual, pula para a próxima
                        if (yAtual + espacoNecessario > alturaPagina - 80)
                        {
                            document.EndPage();
                            canvas = document.BeginPage(larguraPagina, alturaPagina);
                            yAtual = margem + 20;
                            
                            paint.Color = CorPrimaria;
                            canvas.DrawRect(0, 0, 10, alturaPagina, paint);
                        }

                        // Título da Peça
                        paint.Typeface = _fonteBold;
                        paint.TextSize = 13;
                        paint.Color = CorPrimaria;
                        string tituloPeca = (peca.Ambiente ?? "SEM AMBIENTE").ToUpper() + " - " + (peca.PedraNome ?? "Pedra") + " (x" + peca.Quantidade + ")";
                        canvas.DrawText(tituloPeca, margem, yAtual, paint);
                        
                        yAtual += 15;

                        // Quadro de Desenho
                        SKRect rectQuadro = new SKRect(margem, yAtual, larguraPagina - margem, yAtual + alturaQuadro);
                        paint.Style = SKPaintStyle.Fill;
                        paint.Color = CorFundoDesenho;
                        canvas.DrawRoundRect(rectQuadro, 10, 10, paint);
                        
                        // Renderização via Bitmap (PecaDrawable)
                        using (var bitmapPeca = DesenharPecaEmBitmap(peca, isTecnico, (int)rectQuadro.Width - 20, (int)rectQuadro.Height - 20))
                        {
                            SKRect rectDesenho = new SKRect(
                                rectQuadro.Left + 10, 
                                rectQuadro.Top + 10, 
                                rectQuadro.Right - 10, 
                                rectQuadro.Bottom - 10
                            );
                            canvas.DrawBitmap(bitmapPeca, rectDesenho);
                        }
                        
                        // Lista de Corte lateral (apenas técnico)
                        if (isTecnico)
                        {
                            AdicionarListaProdução(canvas, paint, peca, rectQuadro.Right - 130, rectQuadro.Bottom - 65);
                        }
                        
                        yAtual += alturaQuadro + 20;

                        if (isTecnico)
                        {
                            paint.Typeface = _fonteNormal;
                            paint.Color = CorTextoEscuro;
                            paint.TextSize = 10;
                            
                            // Montagem manual da string para evitar erro de interpretação de colchetes
                            string d1 = "MEDIDAS BRUTAS: P1 [" + peca.Largura.ToString("F2") + " x " + peca.Altura.ToString("F2") + "]";
                            if (peca.LarguraP2 > 0.01) 
                            {
                                string lado = string.IsNullOrEmpty(peca.LadoP2) ? "" : " (" + peca.LadoP2 + ")";
                                d1 += " | P2" + lado + " [" + peca.LarguraP2.ToString("F2") + " x " + peca.AlturaP2.ToString("F2") + "]";
                            }
                            if (peca.LarguraP3 > 0.01) 
                            {
                                string lado = string.IsNullOrEmpty(peca.LadoP3) ? "" : " (" + peca.LadoP3 + ")";
                                d1 += " | P3" + lado + " [" + peca.LarguraP3.ToString("F2") + " x " + peca.AlturaP3.ToString("F2") + "]";
                            }
                            
                            canvas.DrawText(d1, margem + 10, yAtual, paint);
                            
                            string acab = "";
                            if (peca.RodobancaP1Tras > 0.01 || peca.RodobancaP1Frente > 0.01 || 
                                peca.RodobancaP1Esquerda > 0.01 || peca.RodobancaP1Direita > 0.01)
                                acab += " RODOBANCA";
                            if (peca.SaiaP1Frente > 0.01 || peca.SaiaP2Frente > 0.01 || peca.SaiaP3Frente > 0.01)
                                acab += " SAIA";
                            
                            if (!string.IsNullOrEmpty(acab))
                            {
                                yAtual += 15;
                                canvas.DrawText("ACABAMENTOS:" + acab, margem + 10, yAtual, paint);
                            }
                        }
                        else
                        {
                            paint.Typeface = _fonteBold;
                            paint.Color = CorPrimaria;
                            paint.TextSize = 12;
                            string valorPeca = "Subtotal da Peça: " + peca.ValorTotalPeca.ToString("C");
                            canvas.DrawText(valorPeca, larguraPagina - margem - paint.MeasureText(valorPeca) - 10, yAtual, paint);
                            totalFinanceiro += peca.ValorTotalPeca;
                        }

                        yAtual += 40;
                    }

                    // --- RODAPÉ FINANCEIRO (Apenas no Orçamento) ---
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

            // Abre o menu de compartilhamento do Android/iOS
            await Share.Default.RequestAsync(new ShareFileRequest
            {
                Title = prefixo,
                File = new ShareFile(caminhoPdf)
            });
        }
        catch (Exception ex) { Debug.WriteLine($"Erro ao gerar PDF: {ex.Message}"); }
    }

    private void DesenharGeometriaPecaMelhorada(SKCanvas canvas, SKRect rect, PecaOrcamento p, bool explodido)
    {
        // Gaps para vista técnica
        float gapPeça = explodido ? 45 : 0;
        
        double largP2 = p.LarguraP2 > 0.01 ? p.LarguraP2 : 0;
        double largP3 = p.LarguraP3 > 0.01 ? p.LarguraP3 : 0;
        double totalW = p.Largura + largP2 + largP3;
        double maxH = Math.Max(p.Altura, Math.Max(p.AlturaP2, p.AlturaP3));

        // Margem interna para não colar nas bordas
        float margemInterna = 35;
        float areaDisponivelLargura = rect.Width - (margemInterna * 2) - (explodido ? (gapPeça * (largP2 > 0.01 ? 1 : 0) + (gapPeça * (largP3 > 0.01 ? 1 : 0))) : 0);
        float areaDisponivelAltura = rect.Height - (margemInterna * 2);

        // Cálculo de escala inteligente com limite mínimo
        float escala = (float)Math.Min(areaDisponivelLargura / totalW, areaDisponivelAltura / maxH);
        
        // Limitar escala máxima para não ficar gigante
        if (escala > 3.5f) escala = 3.5f;
        if (escala < 0.8f) escala = 0.8f;
        
        // Centralização do desenho no quadro
        float larguraDesenho = (float)(totalW * escala) + (explodido ? (gapPeça * (largP2 > 0.01 ? 1 : 0) + (gapPeça * (largP3 > 0.01 ? 1 : 0))) : 0);
        float xBase = rect.Left + (rect.Width - larguraDesenho) / 2;
        float yBase = rect.Top + (rect.Height - (float)(maxH * escala)) / 2;

        using (var paint = new SKPaint { IsAntialias = true, StrokeWidth = 1.5f })
        {
            // 1. Perna Esquerda (P2)
            bool temP2 = largP2 > 0.01 && !string.IsNullOrEmpty(p.LadoP2) && p.LadoP2 == "Esquerda";
            if (temP2)
            {
                SKRect rP2 = new SKRect(xBase, yBase, xBase + (float)(p.LarguraP2 * escala), yBase + (float)(p.AlturaP2 * escala));
                DesenharBlocoPedraMelhorado(canvas, rP2, "P2", p.LarguraP2, p.AlturaP2, paint, explodido, 
                                           p.RodobancaP2Tras, p.SaiaP2Frente, p.RodobancaP2Esquerda, p.SaiaP2Esquerda);
                
                if (explodido) {
                    DesenharLinhaGuiaMelhorada(canvas, rP2.Right, rP2.MidY, rP2.Right + gapPeça, rP2.MidY, paint, "P2-P1");
                    xBase += (float)(p.LarguraP2 * escala) + gapPeça;
                } else {
                    xBase += (float)(p.LarguraP2 * escala);
                }
            }

            // 2. Peça Principal (P1)
            SKRect rP1 = new SKRect(xBase, yBase, xBase + (float)(p.Largura * escala), yBase + (float)(p.Altura * escala));
            DesenharBlocoPedraMelhorado(canvas, rP1, "P1", p.Largura, p.Altura, paint, explodido, 
                                       p.RodobancaP1Tras, p.SaiaP1Frente, p.RodobancaP1Esquerda, p.SaiaP1Esquerda);
            
            xBase += (float)(p.Largura * escala);
            
            // 3. Perna Direita (P2 ou P3)
            bool temP3 = largP3 > 0.01;
            bool temP2Direita = largP2 > 0.01 && p.LadoP2 == "Direita";
            
            if (temP2Direita || temP3)
            {
                if (explodido)
                {
                    DesenharLinhaGuiaMelhorada(canvas, rP1.Right, rP1.MidY, rP1.Right + gapPeça, rP1.MidY, paint, "P1-P" + (temP3 ? "3" : "2"));
                    xBase += gapPeça;
                }
                
                double lD = temP3 ? p.LarguraP3 : p.LarguraP2;
                double aD = temP3 ? p.AlturaP3 : p.AlturaP2;
                string id = temP3 ? "P3" : "P2";
                
                SKRect rDir = new SKRect(xBase, yBase, xBase + (float)(lD * escala), yBase + (float)(aD * escala));
                
                DesenharBlocoPedraMelhorado(canvas, rDir, id, lD, aD, paint, explodido,
                                           temP3 ? p.RodobancaP3Tras : p.RodobancaP2Tras,
                                           temP3 ? p.SaiaP3Frente : p.SaiaP2Frente,
                                           temP3 ? p.RodobancaP3Esquerda : p.RodobancaP2Esquerda,
                                           temP3 ? p.SaiaP3Esquerda : p.SaiaP2Esquerda);
            }

            // Desenhar linha de base de referência (chão/parede)
            paint.Color = CorLinhaCota;
            paint.StrokeWidth = 0.8f;
            paint.PathEffect = SKPathEffect.CreateDash(new float[] { 4, 4 }, 0);
            
            // Linha de base inferior
            float yBaseInferior = yBase + (float)(maxH * escala) + 10;
            canvas.DrawLine(rect.Left + 10, yBaseInferior, rect.Right - 10, yBaseInferior, paint);
            
            // Texto indicativo
            paint.Color = CorTextoCinza;
            paint.TextSize = 8;
            paint.Typeface = _fonteNormal;
            paint.PathEffect = null;
            canvas.DrawText("LINHA DE BASE (PISO)", rect.Left + 20, yBaseInferior - 3, paint);
        }
    }

    private void DesenharBlocoPedraMelhorado(SKCanvas canvas, SKRect r, string id, double w, double h, SKPaint paint, bool explodido, 
                                           double rbT, double saiaF, double rbE, double saiaE)
    {
        // Preenchimento da Pedra com gradiente sutil para dar profundidade
        using (var gradiente = SKShader.CreateLinearGradient(
            new SKPoint(r.Left, r.Top),
            new SKPoint(r.Right, r.Bottom),
            new SKColor[] { SKColors.WhiteSmoke, SKColors.LightGray },
            new float[] { 0, 1 },
            SKShaderTileMode.Clamp))
        {
            paint.Style = SKPaintStyle.Fill;
            paint.Shader = gradiente;
            canvas.DrawRect(r, paint);
            paint.Shader = null;
        }

        // Borda da Pedra mais destacada
        paint.Style = SKPaintStyle.Stroke;
        paint.Color = SKColors.Black;
        paint.StrokeWidth = 1.8f;
        canvas.DrawRect(r, paint);

        // Sombras internas sutis
        paint.Style = SKPaintStyle.Stroke;
        paint.Color = SKColors.Gray;
        paint.StrokeWidth = 0.8f;
        canvas.DrawLine(r.Left + 1, r.Top + 1, r.Right - 1, r.Top + 1, paint);
        canvas.DrawLine(r.Left + 1, r.Top + 1, r.Left + 1, r.Bottom - 1, paint);

        // Texto Identificador em fundo semi-transparente para melhor legibilidade
        paint.Style = SKPaintStyle.Fill;
        paint.Typeface = _fonteBold;
        paint.TextSize = 12;
        paint.Color = SKColors.Black;
        
        // Fundo branco para o texto ID
        float textWidthId = paint.MeasureText(id);
        paint.Style = SKPaintStyle.Fill;
        paint.Color = new SKColor(255, 255, 255, 200); // Branco com transparência
        canvas.DrawRect(r.MidX - textWidthId/2 - 3, r.MidY - 10, textWidthId + 6, 16, paint);
        
        paint.Color = SKColors.Black;
        paint.Style = SKPaintStyle.Fill;
        canvas.DrawText(id, r.MidX - textWidthId/2, r.MidY + 5, paint);
        
        // Medidas em posições otimizadas para não sobrepor
        paint.Typeface = _fonteNormal;
        paint.TextSize = 9;
        paint.Color = CorTextoMedidas;
        
        // Medida horizontal (largura) - acima da peça
        string largStr = $"{w:F2}m";
        float textWidthLarg = paint.MeasureText(largStr);
        
        paint.Style = SKPaintStyle.Fill;
        paint.Color = new SKColor(255, 255, 255, 200); // Branco com transparência
        canvas.DrawRect(r.MidX - textWidthLarg/2 - 2, r.Top - 18, textWidthLarg + 4, 14, paint);
        
        paint.Color = CorTextoMedidas;
        canvas.DrawText(largStr, r.MidX - textWidthLarg/2, r.Top - 8, paint);
        
        // Medida vertical (altura) - à esquerda da peça
        string altStr = $"{h:F2}m";
        float textWidthAlt = paint.MeasureText(altStr);
        
        // Rotacionar canvas para texto vertical usando RotateDegrees
        canvas.Save();
        canvas.Translate(r.Left - 20, r.MidY);
        canvas.RotateDegrees(-90);
        
        paint.Style = SKPaintStyle.Fill;
        paint.Color = new SKColor(255, 255, 255, 200); // Branco com transparência
        canvas.DrawRect(-textWidthAlt/2 - 2, -7, textWidthAlt + 4, 14, paint);
        
        paint.Color = CorTextoMedidas;
        canvas.DrawText(altStr, -textWidthAlt/2, 3, paint);
        canvas.Restore();

        // --- ACABAMENTOS DESPRENDIDOS (Vista Técnica) ---
        float offset = explodido ? 18 : 0;

        // Rodobanca Trás
        if (rbT > 0.01) {
            paint.Color = CorRodobanca;
            paint.StrokeWidth = 4;
            paint.PathEffect = null;
            
            // Linha tracejada para indicar posição real
            if (explodido) {
                paint.StrokeWidth = 1;
                paint.Color = CorSetaGuia;
                paint.PathEffect = SKPathEffect.CreateDash(new float[] { 3, 3 }, 0);
                canvas.DrawLine(r.MidX, r.Top, r.MidX, r.Top - offset, paint);
            }
            
            // Linha do rodobanca
            paint.StrokeWidth = 4;
            paint.Color = CorRodobanca;
            paint.PathEffect = null;
            canvas.DrawLine(r.Left, r.Top - offset, r.Right, r.Top - offset, paint);
            
            // Texto do rodobanca
            paint.TextSize = 8;
            paint.Color = CorRodobanca;
            canvas.DrawText($"RB {rbT:F2}m", r.Left + 5, r.Top - offset - 3, paint);
        }

        // Saia Frente
        if (saiaF > 0.01) {
            paint.Color = CorSaia;
            paint.StrokeWidth = 3.5f;
            
            if (explodido) {
                paint.StrokeWidth = 1;
                paint.Color = CorSetaGuia;
                paint.PathEffect = SKPathEffect.CreateDash(new float[] { 3, 3 }, 0);
                canvas.DrawLine(r.MidX, r.Bottom, r.MidX, r.Bottom + offset, paint);
            }
            
            paint.StrokeWidth = 3.5f;
            paint.Color = CorSaia;
            paint.PathEffect = null;
            canvas.DrawLine(r.Left, r.Bottom + offset, r.Right, r.Bottom + offset, paint);
            
            paint.TextSize = 8;
            paint.Color = CorSaia;
            canvas.DrawText($"SAIA {saiaF:F2}m", r.Left + 5, r.Bottom + offset + 10, paint);
        }
        
        // Rodobanca Lateral Esquerda
        if (rbE > 0.01 && id != "P3") { // Só desenha se for significativo e não for a peça mais à direita
            paint.Color = CorRodobanca;
            paint.StrokeWidth = 4;
            
            float offsetLateral = explodido ? 15 : 0;
            canvas.DrawLine(r.Left - offsetLateral, r.Top, r.Left - offsetLateral, r.Bottom, paint);
            
            if (explodido) {
                paint.StrokeWidth = 1;
                paint.Color = CorSetaGuia;
                paint.PathEffect = SKPathEffect.CreateDash(new float[] { 3, 3 }, 0);
                canvas.DrawLine(r.Left, r.MidY, r.Left - offsetLateral, r.MidY, paint);
            }
        }
    }

    private void DesenharLinhaGuiaMelhorada(SKCanvas canvas, float x1, float y1, float x2, float y2, SKPaint paint, string label)
    {
        paint.Color = CorSetaGuia;
        paint.StrokeWidth = 1f;
        paint.PathEffect = SKPathEffect.CreateDash(new float[] { 4, 3 }, 0);
        canvas.DrawLine(x1, y1, x2, y2, paint);

        // Reset
        paint.PathEffect = null;
        paint.StrokeWidth = 1f;

        // pequena seta início
        canvas.DrawLine(x1, y1, x1 + 4, y1 - 4, paint);
        canvas.DrawLine(x1, y1, x1 + 4, y1 + 4, paint);

        // pequena seta final
        canvas.DrawLine(x2, y2, x2 - 4, y2 - 4, paint);
        canvas.DrawLine(x2, y2, x2 - 4, y2 + 4, paint);
    }
}