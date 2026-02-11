using SQLite;
using Marmorariacentral.Models;

namespace Marmorariacentral.Services
{
    public class DatabaseService
    {
        // O '?' resolve o erro CS8618 (indica que pode ser nulo antes do Init)
        private SQLiteAsyncConnection? _database;
        private readonly string _dbPath;

        public DatabaseService()
        {
            _dbPath = Path.Combine(FileSystem.AppDataDirectory, "marmoraria_v1.db3");
        }

        private async Task Init()
        {
            if (_database is not null)
                return;

            _database = new SQLiteAsyncConnection(_dbPath);

            // Criamos todas as tabelas baseadas nas Models que definimos
            await _database.CreateTablesAsync<Usuario, Orcamento, EstoqueItem, FinanceiroRegistro, Cliente>();
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