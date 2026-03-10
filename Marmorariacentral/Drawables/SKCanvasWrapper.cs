using SkiaSharp;
using Microsoft.Maui.Graphics;

namespace Marmorariacentral.Drawables;

public class SKCanvasWrapper : IDrawingCanvas
{
    private readonly SKCanvas _canvas;
    private readonly SKPaint _paint;
    private readonly Stack<SKMatrix> _matrixStack = new();

    private Color _strokeColor = Colors.Black;
    private Color _fillColor = Colors.Transparent;
    private Color _fontColor = Colors.Black;

    private float _strokeSize = 1;
    private float _fontSize = 12;

    private float[] _strokeDashPattern;

    public SKCanvasWrapper(SKCanvas canvas)
    {
        _canvas = canvas;

        _paint = new SKPaint
        {
            IsAntialias = true,
            StrokeWidth = 1,
            TextSize = 12
        };
    }

    public bool Antialias
    {
        set => _paint.IsAntialias = value;
    }

    public Color StrokeColor
    {
        set => _strokeColor = value;
    }

    public Color FillColor
    {
        set => _fillColor = value;
    }

    public Color FontColor
    {
        set => _fontColor = value;
    }

    public float StrokeSize
    {
        set => _strokeSize = value;
    }

    public float FontSize
    {
        set => _fontSize = value;
    }

    public float[] StrokeDashPattern
    {
        set
        {
            _strokeDashPattern = value;

            if (value == null)
                _paint.PathEffect = null;
            else
                _paint.PathEffect = SKPathEffect.CreateDash(value, 0);
        }
    }

    public void DrawLine(float x1, float y1, float x2, float y2)
    {
        _paint.Style = SKPaintStyle.Stroke;
        _paint.StrokeWidth = _strokeSize;
        _paint.Color = ToSKColor(_strokeColor);

        _canvas.DrawLine(x1, y1, x2, y2, _paint);
    }

    public void DrawRectangle(float x, float y, float width, float height)
    {
        var rect = new SKRect(x, y, x + width, y + height);

        if (_fillColor != Colors.Transparent)
        {
            _paint.Style = SKPaintStyle.Fill;
            _paint.Color = ToSKColor(_fillColor);
            _canvas.DrawRect(rect, _paint);
        }

        if (_strokeColor != Colors.Transparent)
        {
            _paint.Style = SKPaintStyle.Stroke;
            _paint.StrokeWidth = _strokeSize;
            _paint.Color = ToSKColor(_strokeColor);

            _canvas.DrawRect(rect, _paint);
        }
    }

    public void FillRectangle(float x, float y, float width, float height)
    {
        _paint.Style = SKPaintStyle.Fill;
        _paint.Color = ToSKColor(_fillColor);

        _canvas.DrawRect(x, y, width, height, _paint);
    }

    public void DrawString(
        string value,
        float x,
        float y,
        float width,
        float height,
        HorizontalAlignment horizontalAlignment,
        VerticalAlignment verticalAlignment)
    {
        if (string.IsNullOrEmpty(value))
            return;

        _paint.Style = SKPaintStyle.Fill;
        _paint.Color = ToSKColor(_fontColor);
        _paint.TextSize = _fontSize;
        _paint.Typeface = SKTypeface.FromFamilyName("Arial");

        var bounds = new SKRect();
        _paint.MeasureText(value, ref bounds);

        float textX = x;

        if (horizontalAlignment == HorizontalAlignment.Center)
            textX = x + (width - bounds.Width) / 2;

        else if (horizontalAlignment == HorizontalAlignment.Right)
            textX = x + width - bounds.Width;

        var metrics = _paint.FontMetrics;
        float textHeight = metrics.Descent - metrics.Ascent;

        float textY;

        if (verticalAlignment == VerticalAlignment.Center)
            textY = y + (height / 2) + (textHeight / 2) - metrics.Descent;

        else if (verticalAlignment == VerticalAlignment.Bottom)
            textY = y + height - metrics.Descent;

        else
            textY = y - metrics.Ascent;

        _canvas.DrawText(value, textX, textY, _paint);
    }

    public void DrawString(string value, float x, float y, HorizontalAlignment horizontalAlignment)
    {
        DrawString(value, x, y, 200, 40, horizontalAlignment, VerticalAlignment.Top);
    }

    public void SaveState()
    {
        _canvas.Save();
        _matrixStack.Push(_canvas.TotalMatrix);
    }

    public void RestoreState()
    {
        _canvas.Restore();

        if (_matrixStack.Count > 0)
        {
            _canvas.SetMatrix(_matrixStack.Pop());
        }
    }

    public void Translate(float tx, float ty)
    {
        _canvas.Translate(tx, ty);
    }

    public void Rotate(float degrees)
    {
        _canvas.RotateDegrees(degrees);
    }

    private static SKColor ToSKColor(Color color)
    {
        return new SKColor(
            (byte)(color.Red * 255),
            (byte)(color.Green * 255),
            (byte)(color.Blue * 255),
            (byte)(color.Alpha * 255));
    }
}