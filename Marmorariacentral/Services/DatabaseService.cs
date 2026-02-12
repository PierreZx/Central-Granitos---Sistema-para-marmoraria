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
            // Mantendo o caminho definitivo para não perder dados locais
            _dbPath = Path.Combine(FileSystem.AppDataDirectory, "marmoraria_definitiva.db3");
        }

        private async Task Init()
        {
            if (_database is not null) return;

            _database = new SQLiteAsyncConnection(_dbPath);

            // CORREÇÃO CS1503: Adicionado 'CreateFlags.None' como primeiro argumento.
            // Isso informa ao SQLite como proceder e permite listar os tipos logo em seguida.
            await _database.CreateTablesAsync(
                CreateFlags.None, 
                typeof(Usuario), 
                typeof(Orcamento), 
                typeof(EstoqueItem), 
                typeof(FinanceiroRegistro), 
                typeof(Cliente), 
                typeof(PecaOrcamento));
        }

        public async Task<List<T>> GetItemsAsync<T>() where T : new()
        {
            await Init();
            return await _database!.Table<T>().ToListAsync();
        }

        public async Task<int> SaveItemAsync<T>(T item) where T : new()
        {
            await Init();
            return await _database!.InsertOrReplaceAsync(item);
        }

        public async Task<int> DeleteItemAsync<T>(T item) where T : new()
        {
            await Init();
            return await _database!.DeleteAsync(item);
        }
    }
}