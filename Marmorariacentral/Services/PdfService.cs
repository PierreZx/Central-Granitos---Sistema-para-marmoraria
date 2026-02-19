using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;
using QuestPDF.Drawing;
using QuestPDF.Elements;
using System.Globalization;
using Marmorariacentral.Models;
using Microsoft.Maui.ApplicationModel;
using Marmorariacentral.ViewModels;
using Marmorariacentral.Drawables;
using Microsoft.Maui.Graphics;
using Microsoft.Maui.Graphics.Platform;
using System.IO;
using System.Diagnostics;

// DEFINIÇÃO DE ALIASES PARA RESOLVER CS0104 (Ambiguidade)
using MauiColors = Microsoft.Maui.Graphics.Colors;
using PdfColors = QuestPDF.Helpers.Colors;

namespace Marmorariacentral.Services;

public class PdfService
{
    private readonly DatabaseService _dbService;
    
    // Cores de Identidade Visual (Vermelho Central)
    private const string CorPrimaria = "#8B1A1A"; 
    private const string CorSecundaria = "#2C3E50"; 
    private const string CorDestaque = "#27AE60"; 
    private const string CorFundo = "#F8F9FA";
    private const string CorBorda = "#E0E0E0";

    public PdfService(DatabaseService dbService)
    {
        _dbService = dbService;
        QuestPDF.Settings.License = LicenseType.Community;
    }

    /// <summary>
    /// Gera o Orçamento em PDF com desenhos técnicos e abre automaticamente.
    /// </summary>
    public async Task<string> GerarOrcamentoPdfAsync(Orcamento model, List<PecaOrcamento> pecas)
    {
        try
        {
            var filePath = Path.Combine(FileSystem.AppDataDirectory, $"Orcamento_{model.Id}_{DateTime.Now:yyyyMMddHHmmss}.pdf");

            // 1. CARREGAR LOGO
            byte[] logoBytes = await CarregarLogoAsync();
            
            // 2. GERAR DESENHOS TÉCNICOS (Síncrono para evitar CS1998)
            var desenhosPecas = GerarDesenhosPecas(pecas);

            // 3. CONSTRUÇÃO DO DOCUMENTO QUESTPDF
            Document.Create(container =>
            {
                container.Page(page =>
                {
                    page.Margin(30);
                    page.Size(PageSizes.A4);
                    page.PageColor(PdfColors.White); // Uso do Alias PdfColors
                    
                    // --- CABEÇALHO ---
                    page.Header().Column(header =>
                    {
                        header.Item().Row(row =>
                        {
                            if (logoBytes.Length > 0)
                            {
                                row.ConstantItem(100).Height(70).Image(logoBytes).FitArea();
                            }
                            
                            row.RelativeItem().PaddingLeft(20).Column(col =>
                            {
                                col.Item().Text("CENTRAL GRANITOS").FontSize(26).Bold().FontColor(CorPrimaria);
                                col.Item().Text("Mármores, Granitos e Pedras Decorativas").FontSize(11).FontColor(CorSecundaria).Italic();
                                col.Item().PaddingTop(5).Text("Praça Presidente Getúlio Vargas, 129 - Centro").FontSize(9);
                                col.Item().Text("Carmo do Cajuru - MG | CEP: 35515-000").FontSize(9);
                            });
                            
                            row.ConstantItem(160).Column(col =>
                            {
                                col.Item().Background(CorPrimaria).Padding(5).AlignCenter().Text("ORÇAMENTO").FontSize(16).Bold().FontColor(PdfColors.White);
                                col.Item().PaddingTop(5).AlignRight().Text($"Nº: {model.Id.Substring(0, 8).ToUpper()}").FontSize(9).Bold();
                                col.Item().AlignRight().Text($"Data: {model.DataCriacao:dd/MM/yyyy}").FontSize(9);
                            });
                        });
                        
                        header.Item().PaddingVertical(10).LineHorizontal(1.5f).LineColor(CorPrimaria);
                    });

                    // --- CONTEÚDO ---
                    page.Content().Column(content =>
                    {
                        content.Item().PaddingBottom(15).Row(row =>
                        {
                            row.RelativeItem().Column(c =>
                            {
                                c.Item().Text("SOLICITANTE").FontSize(10).Bold().FontColor(CorPrimaria);
                                c.Item().Text(model.NomeCliente).FontSize(12).Bold();
                                c.Item().Text($"Contato: {model.Contato}").FontSize(10);
                                c.Item().Text($"Endereço: {model.Endereco}").FontSize(10);
                            });

                            row.RelativeItem().AlignRight().Column(c =>
                            {
                                c.Item().Text("CONTATOS DA LOJA").FontSize(10).Bold().FontColor(CorPrimaria);
                                c.Item().Text("📞 (37) 98407-2955").FontSize(10);
                                c.Item().Text("📞 (37) 98412-7829").FontSize(10);
                            });
                        });

                        content.Item().Text("DETALHAMENTO TÉCNICO DAS PEÇAS").FontSize(14).Bold().FontColor(CorPrimaria).Underline();

                        foreach (var peca in pecas)
                        {
                            content.Item().PaddingTop(15).Border(0.5f).BorderColor(CorBorda).Background(PdfColors.White).Column(pecaCard =>
                            {
                                pecaCard.Item().Background("#F2F2F2").Padding(8).Row(h =>
                                {
                                    h.RelativeItem().Text($"{peca.Ambiente.ToUpper()} - {peca.PedraNome}").FontSize(11).Bold().FontColor(CorPrimaria);
                                    h.RelativeItem().AlignRight().Text($"Subtotal: {peca.ValorTotalPeca:C}").FontSize(11).Bold().FontColor(CorDestaque);
                                });

                                pecaCard.Item().Padding(10).Row(row =>
                                {
                                    row.RelativeItem(1.5f).Column(info =>
                                    {
                                        info.Spacing(3);
                                        info.Item().Text("DIMENSÕES PLANAS").FontSize(9).Bold().FontColor(CorSecundaria);
                                        info.Item().Text($"• P1 (Principal): {peca.Largura:F2}m x {peca.Altura:F2}m").FontSize(9);
                                        
                                        if (peca.LarguraP2 > 0.01)
                                            info.Item().Text($"• P2 (L - {peca.LadoP2}): {peca.LarguraP2:F2}m x {peca.AlturaP2:F2}m").FontSize(9);
                                        
                                        if (peca.LarguraP3 > 0.01)
                                            info.Item().Text($"• P3 (U): {peca.LarguraP3:F2}m x {peca.AlturaP3:F2}m").FontSize(9);

                                        info.Item().PaddingTop(5).Text("ACABAMENTOS").FontSize(9).Bold().FontColor(CorSecundaria);
                                        if (peca.RodobancaP1Tras > 0 || peca.RodobancaP1Esquerda > 0)
                                            info.Item().Text($"• Rodobanca: Altura {peca.RodobancaP1Tras:F2}m").FontSize(9);
                                        if (peca.SaiaP1Frente > 0)
                                            info.Item().Text($"• Saia/Borda: Altura {peca.SaiaP1Frente:F2}m").FontSize(9);

                                        if (peca.TemBojo || peca.TemCooktop)
                                        {
                                            info.Item().PaddingTop(5).Text("RECORTES").FontSize(9).Bold().FontColor(CorSecundaria);
                                            if (peca.TemBojo) info.Item().Text($"• Recorte de Cuba na {peca.PecaDestinoBojo}").FontSize(9);
                                            if (peca.TemCooktop) info.Item().Text($"• Recorte de Cooktop na {peca.PecaDestinoCooktop}").FontSize(9);
                                        }
                                        
                                        info.Item().PaddingTop(5).Row(r => {
                                            r.AutoItem().Text("QUANTIDADE: ").FontSize(9).Bold();
                                            r.AutoItem().Text($"{peca.Quantidade} Unidade(s)").FontSize(9);
                                        });
                                    });

                                    // Coluna de Desenho
                                    if (desenhosPecas.TryGetValue(peca.Id, out var imgBytes))
                                    {
                                        row.RelativeItem(1).PaddingLeft(10).Column(drawCol =>
                                        {
                                            drawCol.Item().AlignCenter().Text("VISTA SUPERIOR (ESQUEMA)").FontSize(8).Bold().FontColor(PdfColors.Grey.Medium);
                                            drawCol.Item().Height(150).Image(imgBytes).FitArea();
                                            drawCol.Item().PaddingTop(5).AlignCenter().Text("⬜ P1 | 🟦 L | 🟩 Rodobanca | 🟨 Saia").FontSize(7);
                                        });
                                    }
                                });
                            });
                        }

                        // --- RESUMO ---
                        content.Item().PaddingTop(30).AlignRight().Container().Width(250).Column(res =>
                        {
                            res.Item().Row(r => {
                                r.RelativeItem().Text("Soma Bruta das Peças:").FontSize(11);
                                r.RelativeItem().AlignRight().Text(model.ValorTotal.ToString("C")).FontSize(11);
                            });
                            res.Item().PaddingTop(5).Background(CorPrimaria).Padding(8).Row(r => {
                                r.RelativeItem().Text("VALOR TOTAL FINAL").FontSize(13).Bold().FontColor(PdfColors.White);
                                r.RelativeItem().AlignRight().Text(model.ValorTotal.ToString("C")).FontSize(13).Bold().FontColor(PdfColors.White);
                            });
                        });

                        // --- NOTAS ---
                        content.Item().PaddingTop(40).Column(notas =>
                        {
                            notas.Spacing(2);
                            notas.Item().Text("CONDIÇÕES GERAIS").FontSize(11).Bold().FontColor(CorPrimaria);
                            notas.Item().Text("1. Prazo de Entrega: De 15 a 20 dias úteis após conferência das medidas.").FontSize(9);
                            notas.Item().Text("2. Garantia: 05 anos contra defeitos de fabricação ou instalação.").FontSize(9);
                            notas.Item().Text("3. Validade: Este orçamento é válido por 07 dias corridos.").FontSize(9);
                            notas.Item().PaddingTop(15).AlignCenter().Text("____________________________________________________").FontSize(10);
                            notas.Item().AlignCenter().Text("Assinatura do Cliente").FontSize(9);
                        });
                    });

                    // --- RODAPÉ ---
                    page.Footer().Column(footer =>
                    {
                        footer.Item().PaddingTop(10).LineHorizontal(0.5f).LineColor(CorBorda);
                        footer.Item().PaddingTop(5).Row(row =>
                        {
                            row.RelativeItem().Text("Central Granitos - Qualidade e Tradição").FontSize(8).FontColor(PdfColors.Grey.Medium);
                            row.RelativeItem().AlignRight().Text(t =>
                            {
                                t.Span("Página ").FontSize(8);
                                t.CurrentPageNumber().FontSize(8);
                                t.Span(" de ").FontSize(8);
                                t.TotalPages().FontSize(8);
                            });
                        });
                    });
                });
            }).GeneratePdf(filePath);

            await Launcher.OpenAsync(new OpenFileRequest { File = new ReadOnlyFile(filePath) });
            return filePath;
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"ERRO CRÍTICO PDF: {ex.Message}");
            throw;
        }
    }

    private async Task<byte[]> CarregarLogoAsync()
    {
        try
        {
            using var stream = await FileSystem.OpenAppPackageFileAsync("logo_central.png");
            using var ms = new MemoryStream();
            await stream.CopyToAsync(ms);
            return ms.ToArray();
        }
        catch { return Array.Empty<byte>(); }
    }

    // GERAÇÃO DE IMAGENS CORRIGIDA PARA WINDOWS
    private Dictionary<string, byte[]> GerarDesenhosPecas(List<PecaOrcamento> pecas)
    {
        var desenhos = new Dictionary<string, byte[]>();
        foreach (var peca in pecas)
        {
            try
            {
                var tempVm = new CalculadoraPecaViewModel(_dbService);
                tempVm.Peca = peca;
                tempVm.LarguraInput = peca.Largura.ToString();
                tempVm.AlturaInput = peca.Altura.ToString();
                tempVm.LarguraP2Input = peca.LarguraP2.ToString();
                tempVm.AlturaP2Input = peca.AlturaP2.ToString();
                tempVm.LadoP2 = peca.LadoP2;

                var drawable = new PecaDrawable(tempVm);
                int w = 600; int h = 450;

                // SOLUÇÃO CS0234: Usar PlatformBitmapExportContext com namespace completo
                using var context = new Microsoft.Maui.Graphics.Platform.PlatformBitmapExportContext(w, h, 1);
                var canvas = context.Canvas;

                canvas.FillColor = MauiColors.White; // Uso do Alias MauiColors
                canvas.FillRectangle(0, 0, w, h);
                drawable.Draw(canvas, new RectF(0, 0, w, h));

                using var image = context.Image;
                using var ms = new MemoryStream();
                image.Save(ms);
                desenhos[peca.Id] = ms.ToArray();
            }
            catch (Exception ex) { Debug.WriteLine($"Erro desenho peça {peca.Id}: {ex.Message}"); }
        }
        return desenhos;
    }
}