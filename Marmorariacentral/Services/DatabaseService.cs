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
            // Mantivemos o nome do arquivo para preservar os registros financeiros que seu pai já lançou
            _dbPath = Path.Combine(FileSystem.AppDataDirectory, "marmoraria_definitiva.db3");
        }

        private async Task Init()
        {
            if (_database is not null) return;

            _database = new SQLiteAsyncConnection(_dbPath);

            // Criamos apenas as tabelas necessárias para a nova fase do app:
            // 1. Usuario: Para controle de acesso.
            // 2. FinanceiroRegistro: Para todo o controle de entrada, saída e fluxo de caixa.
            await _database.CreateTablesAsync(
                CreateFlags.None, 
                typeof(Usuario), 
                typeof(FinanceiroRegistro));
        }

        /// <summary>
        /// Busca todos os itens de uma tabela.
        /// </summary>
        public async Task<List<T>> GetItemsAsync<T>() where T : new()
        {
            await Init();
            return await _database!.Table<T>().ToListAsync();
        }

        /// <summary>
        /// Salva ou atualiza um registro (Insert or Replace).
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
        /// Método extra para limpar dados antigos se necessário.
        /// </summary>
        public async Task DropLegacyTablesAsync()
        {
            await Init();
            // Estes comandos removem as tabelas antigas do arquivo .db3 para liberar espaço
            await _database!.ExecuteAsync("DROP TABLE IF EXISTS Orcamento");
            await _database!.ExecuteAsync("DROP TABLE IF EXISTS EstoqueItem");
            await _database!.ExecuteAsync("DROP TABLE IF EXISTS Cliente");
            await _database!.ExecuteAsync("DROP TABLE IF EXISTS PecaOrcamento");
        }
    }
}