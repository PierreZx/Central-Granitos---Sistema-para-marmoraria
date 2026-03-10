using SkiaSharp;
using Microsoft.Maui.Graphics;
using Marmorariacentral.Drawables;

namespace Marmorariacentral.Drawables
{
    public class SkiaCanvasAdapter : IDrawingCanvas
    {
        private readonly SKCanvas _canvas;

        private readonly SKPaint strokePaint = new() { IsAntialias = true, Style = SKPaintStyle.Stroke };
        private readonly SKPaint fillPaint = new() { IsAntialias = true, Style = SKPaintStyle.Fill };
        private readonly SKPaint textPaint = new() { IsAntialias = true };

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
            if (string.IsNullOrEmpty(value))
                return;

            var bounds = new SKRect();
            textPaint.MeasureText(value, ref bounds);

            float textX = x;
            float textY = y;

            if (hAlign == HorizontalAlignment.Center)
                textX = x + (w - bounds.Width) / 2;

            if (hAlign == HorizontalAlignment.Right)
                textX = x + w - bounds.Width;

            var metrics = textPaint.FontMetrics;
            float textHeight = metrics.Descent - metrics.Ascent;

            if (vAlign == VerticalAlignment.Center)
                textY = y + (h / 2) + (textHeight / 2) - metrics.Descent;

            else if (vAlign == VerticalAlignment.Bottom)
                textY = y + h - metrics.Descent;

            else
                textY = y - metrics.Ascent;

            _canvas.DrawText(value, textX, textY, textPaint);
        }

        public void DrawString(string value, float x, float y, HorizontalAlignment align)
        {
            var bounds = new SKRect();
            textPaint.MeasureText(value, ref bounds);

            float textX = x;

            if (align == HorizontalAlignment.Center)
                textX = x - bounds.Width / 2;

            if (align == HorizontalAlignment.Right)
                textX = x - bounds.Width;

            _canvas.DrawText(value, textX, y, textPaint);
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