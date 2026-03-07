using SkiaSharp;
using Microsoft.Maui.Graphics;
using Marmorariacentral.Drawables;

namespace Marmorariacentral.Drawables;

public class SKCanvasWrapper : IDrawingCanvas
{
    private readonly SKCanvas _canvas;
    private SKPaint _currentPaint;
    private Stack<SKMatrix> _matrixStack;

    // Propriedades necessárias pela interface
    public bool Antialias 
    { 
        set 
        { 
            // SKCanvas não tem propriedade Antialias direta, usamos SKPaint para isso
            if (_currentPaint != null)
                _currentPaint.IsAntialias = value;
        } 
    }

    private Color _strokeColor;
    public Color StrokeColor 
    { 
        set 
        {
            _strokeColor = value;
            if (_currentPaint != null)
                _currentPaint.Color = ToSKColor(value);
        } 
    }

    private Color _fillColor;
    public Color FillColor 
    { 
        set 
        {
            _fillColor = value;
            // Não aplicamos diretamente, será usado nos métodos Fill
        } 
    }

    private Color _fontColor;
    public Color FontColor 
    { 
        set 
        {
            _fontColor = value;
            if (_currentPaint != null)
                _currentPaint.Color = ToSKColor(value);
        } 
    }

    private float _strokeSize;
    public float StrokeSize 
    { 
        set 
        {
            _strokeSize = value;
            if (_currentPaint != null)
                _currentPaint.StrokeWidth = value;
        } 
    }

    private float _fontSize;
    public float FontSize 
    { 
        set 
        {
            _fontSize = value;
            if (_currentPaint != null)
                _currentPaint.TextSize = value;
        } 
    }

    private float[] _strokeDashPattern;
    public float[] StrokeDashPattern 
    { 
        set 
        {
            _strokeDashPattern = value;
            if (_currentPaint != null && value != null)
                _currentPaint.PathEffect = SKPathEffect.CreateDash(value, 0);
            else if (_currentPaint != null)
                _currentPaint.PathEffect = null;
        } 
    }

    public SKCanvasWrapper(SKCanvas canvas)
    {
        _canvas = canvas;
        _currentPaint = new SKPaint { IsAntialias = true };
        _matrixStack = new Stack<SKMatrix>();
        
        // Valores padrão
        _strokeColor = Colors.Black;
        _fillColor = Colors.White;
        _fontColor = Colors.Black;
        _strokeSize = 1;
        _fontSize = 12;
    }

    public void DrawLine(float x1, float y1, float x2, float y2)
    {
        _currentPaint.Style = SKPaintStyle.Stroke;
        _currentPaint.StrokeWidth = _strokeSize;
        _currentPaint.Color = ToSKColor(_strokeColor);
        
        _canvas.DrawLine(x1, y1, x2, y2, _currentPaint);
    }

    public void DrawRectangle(float x, float y, float width, float height)
    {
        var rect = new SKRect(x, y, x + width, y + height);
        
        // Primeiro preenche se houver cor de preenchimento
        if (_fillColor != null && _fillColor != Colors.Transparent)
        {
            _currentPaint.Style = SKPaintStyle.Fill;
            _currentPaint.Color = ToSKColor(_fillColor);
            _canvas.DrawRect(rect, _currentPaint);
        }
        
        // Depois desenha o contorno
        if (_strokeColor != null && _strokeColor != Colors.Transparent)
        {
            _currentPaint.Style = SKPaintStyle.Stroke;
            _currentPaint.StrokeWidth = _strokeSize;
            _currentPaint.Color = ToSKColor(_strokeColor);
            if (_strokeDashPattern != null)
                _currentPaint.PathEffect = SKPathEffect.CreateDash(_strokeDashPattern, 0);
            
            _canvas.DrawRect(rect, _currentPaint);
            
            if (_strokeDashPattern != null)
                _currentPaint.PathEffect = null;
        }
    }

    public void FillRectangle(float x, float y, float width, float height)
    {
        _currentPaint.Style = SKPaintStyle.Fill;
        _currentPaint.Color = ToSKColor(_fillColor);
        _canvas.DrawRect(new SKRect(x, y, x + width, y + height), _currentPaint);
    }

    public void DrawString(string value, float x, float y, float width, float height, 
        HorizontalAlignment horizontalAlignment, VerticalAlignment verticalAlignment)
    {
        if (string.IsNullOrEmpty(value)) return;

        _currentPaint.Style = SKPaintStyle.Fill;
        _currentPaint.Color = ToSKColor(_fontColor);
        _currentPaint.TextSize = _fontSize;
        _currentPaint.Typeface = SKTypeface.FromFamilyName("Arial");

        var bounds = new SKRect();
        _currentPaint.MeasureText(value, ref bounds);

        float textX = x;
        float textY = y;

        switch (horizontalAlignment)
        {
            case HorizontalAlignment.Center:
                textX = x + (width - bounds.Width) / 2;
                break;
            case HorizontalAlignment.Right:
                textX = x + width - bounds.Width;
                break;
        }

        switch (verticalAlignment)
        {
            case VerticalAlignment.Center:
                textY = y + (height + bounds.Height) / 2;
                break;
            case VerticalAlignment.Bottom:
                textY = y + height;
                break;
        }

        _canvas.DrawText(value, textX, textY, _currentPaint);
    }

    public void DrawString(string value, float x, float y, HorizontalAlignment horizontalAlignment)
    {
        DrawString(value, x, y, 100, 20, horizontalAlignment, VerticalAlignment.Top);
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

    private SKColor ToSKColor(Color color)
    {
        if (color == null) return SKColors.Black;
        return new SKColor(
            (byte)(color.Red * 255),
            (byte)(color.Green * 255),
            (byte)(color.Blue * 255),
            (byte)(color.Alpha * 255)
        );
    }
}