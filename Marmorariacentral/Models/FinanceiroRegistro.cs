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
        
        // Controle de recorrência (Mensal ou Parcelado)
        public bool IsFixo { get; set; } = false; 
        public bool IsParcelado { get; set; } = false;
        public int ParcelaAtual { get; set; } = 1;
        public int TotalParcelas { get; set; } = 1;
        public int DiaVencimentoFixo { get; set; } // Ex: Todo dia 10

        [Ignore] // Usada para exibir "Conta (1/10)" na lista sem alterar o nome original no banco
        public string DescricaoDisplay { get; set; } = string.Empty;

        [Ignore] // Propriedade visual para a bolinha colorida (não persiste no SQLite)
        public Color StatusColor { get; set; } = Colors.Green;
    }
}