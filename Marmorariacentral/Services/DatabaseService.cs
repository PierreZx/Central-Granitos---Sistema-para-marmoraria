using SQLite;
using Marmorariacentral.Models;

namespace Marmorariacentral.Services
{
    public class DatabaseService
    {
        private SQLiteAsyncConnection? _database;
        private readonly string _dbPath;

        public DatabaseService()
        {
            // Mantendo o caminho definitivo para preservar os registros que seu pai já lançou
            _dbPath = Path.Combine(FileSystem.AppDataDirectory, "marmoraria_definitiva.db3");
        }

        private async Task Init()
        {
            if (_database is not null) return;

            _database = new SQLiteAsyncConnection(_dbPath);

            // Criamos todas as tabelas necessárias para o ecossistema completo da marmoraria.
            // O SQLite não apaga dados existentes ao chamar este método, apenas cria o que falta.
            await _database.CreateTablesAsync(
                CreateFlags.None, 
                typeof(Usuario), 
                typeof(FinanceiroRegistro),
                typeof(EstoqueItem),
                typeof(Cliente),
                typeof(PecaOrcamento),
                typeof(Orcamento));
        }

        /// <summary>
        /// Busca todos os itens de uma tabela específica.
        /// </summary>
        public async Task<List<T>> GetItemsAsync<T>() where T : new()
        {
            await Init();
            return await _database!.Table<T>().ToListAsync();
        }

        /// <summary>
        /// Salva ou atualiza um registro (Insert or Replace) baseado na Chave Primária [PrimaryKey].
        /// </summary>
        public async Task<int> SaveItemAsync<T>(T item) where T : new()
        {
            await Init();
            return await _database!.InsertOrReplaceAsync(item);
        }

        /// <summary>
        /// Remove um registro do banco de dados local.
        /// </summary>
        public async Task<int> DeleteItemAsync<T>(T item) where T : new()
        {
            await Init();
            return await _database!.DeleteAsync(item);
        }

        /// <summary>
        /// Método de utilidade para limpar tabelas específicas se necessário.
        /// Use com cautela para não apagar dados importantes.
        /// </summary>
        public async Task DropTableAsync<T>() where T : new()
        {
            await Init();
            await _database!.DropTableAsync<T>();
        }
    }
}