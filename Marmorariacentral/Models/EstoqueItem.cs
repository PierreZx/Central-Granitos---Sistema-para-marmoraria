using SQLite;

namespace Marmorariacentral.Models
{
    public class EstoqueItem
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();

        // Inicializamos com string.Empty para resolver o erro CS8618 
        // e garantir que nunca seja nulo ao salvar no banco.
        public string NomeChapa { get; set; } = string.Empty;

        public double MetroQuadradoTotal { get; set; }

        public double ValorPorMetro { get; set; }

        public int QuantidadeChapas { get; set; }

        public bool IsSynced { get; set; } = false;
    }
}