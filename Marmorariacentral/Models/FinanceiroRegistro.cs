using SQLite;

namespace Marmorariacentral.Models
{
    public class FinanceiroRegistro
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public string Descricao { get; set; } = string.Empty;
        public double Valor { get; set; }
        public DateTime DataVencimento { get; set; }
        public bool FoiPago { get; set; } = false;
        public string Tipo { get; set; } = "Saida"; // Entrada ou Saida
        public bool IsFixo { get; set; } = false;
    }
}