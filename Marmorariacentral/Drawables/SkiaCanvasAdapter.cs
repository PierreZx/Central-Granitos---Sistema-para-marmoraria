using SkiaSharp;
using Microsoft.Maui.Graphics;
using Marmorariacentral.Drawables;

namespace Marmorariacentral.Drawables
{
    public class SkiaCanvasAdapter : IDrawingCanvas
    {
        private readonly SKCanvas _canvas;

        private SKPaint strokePaint = new SKPaint { IsAntialias = true, Style = SKPaintStyle.Stroke };
        private SKPaint fillPaint = new SKPaint { IsAntialias = true, Style = SKPaintStyle.Fill };
        private SKPaint textPaint = new SKPaint { IsAntialias = true };

        public SkiaCanvasAdapter(SKCanvas canvas)
        {
            _canvas = canvas;
        }

        public bool Antialias
        {
            set
            {
                strokePaint.IsAntialias = value;
                fillPaint.IsAntialias = value;
                textPaint.IsAntialias = value;
            }
        }

        public Color StrokeColor
        {
            set => strokePaint.Color = ConverterCor(value);
        }

        public Color FillColor
        {
            set => fillPaint.Color = ConverterCor(value);
        }

        public Color FontColor
        {
            set => textPaint.Color = ConverterCor(value);
        }

        public float StrokeSize
        {
            set => strokePaint.StrokeWidth = value;
        }

        public float FontSize
        {
            set => textPaint.TextSize = value;
        }

        public float[] StrokeDashPattern
        {
            set
            {
                if (value == null)
                    strokePaint.PathEffect = null;
                else
                    strokePaint.PathEffect = SKPathEffect.CreateDash(value, 0);
            }
        }

        public void DrawLine(float x1, float y1, float x2, float y2)
            => _canvas.DrawLine(x1, y1, x2, y2, strokePaint);

        public void DrawRectangle(float x, float y, float w, float h)
            => _canvas.DrawRect(x, y, w, h, strokePaint);

        public void FillRectangle(float x, float y, float w, float h)
            => _canvas.DrawRect(x, y, w, h, fillPaint);

        public void DrawString(string value, float x, float y, float w, float h,
            HorizontalAlignment hAlign, VerticalAlignment vAlign)
        {
            var bounds = new SKRect();
            textPaint.MeasureText(value, ref bounds);

            float tx = x + (w - bounds.Width) / 2;
            float ty = y + (h + bounds.Height) / 2;

            _canvas.DrawText(value, tx, ty, textPaint);
        }

        public void DrawString(string value, float x, float y, HorizontalAlignment align)
        {
            _canvas.DrawText(value, x, y, textPaint);
        }

        public void SaveState() => _canvas.Save();
        public void RestoreState() => _canvas.Restore();
        public void Translate(float tx, float ty) => _canvas.Translate(tx, ty);
        public void Rotate(float degrees) => _canvas.RotateDegrees(degrees);

        private SKColor ConverterCor(Color cor)
        {
            return new SKColor(
                (byte)(cor.Red * 255),
                (byte)(cor.Green * 255),
                (byte)(cor.Blue * 255),
                (byte)(cor.Alpha * 255));
        }
    }
}