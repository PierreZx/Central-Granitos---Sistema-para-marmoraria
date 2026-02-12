using SQLite;

namespace Marmorariacentral.Models
{
    public class PecaOrcamento
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Indexed] // Facilita a busca por cliente
        public string ClienteId { get; set; } = string.Empty;
        
        public string Ambiente { get; set; } = string.Empty;
        public string PedraNome { get; set; } = string.Empty;
        public double ValorM2 { get; set; }
        public double Largura { get; set; }
        public double Altura { get; set; }
        public double ValorTotalPeca { get; set; }
    }
}