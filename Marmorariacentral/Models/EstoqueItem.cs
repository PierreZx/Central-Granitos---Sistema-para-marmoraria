using SQLite;

namespace Marmorariacentral.Models
{
    public class EstoqueItem
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        public string NomeChapa { get; set; } = string.Empty;
        public double QuantidadeChapas { get; set; }
        public double MetroQuadradoTotal { get; set; }
        public double ValorPorMetro { get; set; }
        
        public bool IsSynced { get; set; } = false;
    }
}