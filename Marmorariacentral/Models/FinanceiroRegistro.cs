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
        
        // Novos campos para sua lógica
        public bool IsFixo { get; set; } = false; // Mensal
        public bool IsParcelado { get; set; } = false;
        public int ParcelaAtual { get; set; } = 1;
        public int TotalParcelas { get; set; } = 1;
        public int DiaVencimentoFixo { get; set; } // Para contas de "todo dia 10"

        [Ignore] // Não salva no banco, apenas para a bolinha da interface
        public Color StatusColor { get; set; } = Colors.Green;
    }
}