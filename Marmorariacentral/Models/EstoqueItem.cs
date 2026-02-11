using SQLite;

namespace Marmorariacentral.Models
{
    public class EstoqueItem
    {
        [PrimaryKey]
        public string Id { get; set; } = Guid.NewGuid().ToString();

        public string NomeChapa { get; set; } = string.Empty;

        public double MetroQuadradoTotal { get; set; }

        public double ValorPorMetro { get; set; }

        public int QuantidadeChapas { get; set; }

        public bool IsSynced { get; set; } = false;

        // Propriedade profissional para exibição no Picker da Calculadora
        [Ignore]
        public string DisplayInfo => $"{NomeChapa} - {ValorPorMetro:C}/m²";
    }
}