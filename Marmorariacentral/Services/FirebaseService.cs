using Google.Cloud.Firestore;
using Marmorariacentral.Models;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;
using System.IO;

namespace Marmorariacentral.Services
{
    public class FirebaseService
    {
        private FirestoreDb? _db;
        private readonly string _projectId = "marmoraria-app";
        private readonly string _keyFileName = "firebase_key.json";

        public FirebaseService()
        {
            // A inicialização real ocorre no Init para garantir que o arquivo seja lido
        }

        private async Task Init()
        {
            if (_db != null) return;

            try
            {
                // Carrega o arquivo JSON das credenciais que você salvou em Resources/Raw
                using var stream = await FileSystem.OpenAppPackageFileAsync(_keyFileName);
                using var reader = new StreamReader(stream);
                var jsonContents = await reader.ReadToEndAsync();

                // Define a variável de ambiente necessária para o SDK do Google encontrar a chave
                string tempPath = Path.Combine(FileSystem.CacheDirectory, _keyFileName);
                File.WriteAllText(tempPath, jsonContents);
                Environment.SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", tempPath);

                _db = await FirestoreDb.CreateAsync(_projectId);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Erro ao inicializar Firebase: {ex.Message}");
            }
        }

        // --- SALVAR NO ESTOQUE ---
        public async Task SaveEstoqueAsync(EstoqueItem item)
        {
            await Init();
            if (_db == null) return;

            DocumentReference docRef = _db.Collection("estoque").Document(item.Id);
            
            var data = new Dictionary<string, object>
            {
                { "nome", item.NomeChapa },
                { "quantidade", item.QuantidadeChapas },
                { "metros", item.MetroQuadradoTotal },
                { "preco_m2", item.ValorPorMetro }
            };

            await docRef.SetAsync(data);
        }

        // --- SALVAR ORÇAMENTO ---
        public async Task SaveOrcamentoAsync(Orcamento orcamento)
        {
            await Init();
            if (_db == null) return;

            DocumentReference docRef = _db.Collection("orcamentos").Document(orcamento.Id);

            var data = new Dictionary<string, object>
            {
                { "nome_cliente", orcamento.NomeCliente },
                { "contato", orcamento.Contato },
                { "valor_total", orcamento.ValorTotal },
                { "status", orcamento.Status },
                { "data_criacao", Timestamp.FromDateTime(orcamento.DataCriacao.ToUniversalTime()) }
            };

            await docRef.SetAsync(data);
        }

        // --- RESETAR COLEÇÃO (LIMPAR DADOS ANTIGOS) ---
        public async Task ResetCollectionAsync(string collectionName)
        {
            await Init();
            if (_db == null) return;

            CollectionReference collection = _db.Collection(collectionName);
            QuerySnapshot snapshot = await collection.GetSnapshotAsync();

            foreach (DocumentSnapshot document in snapshot.Documents)
            {
                await document.Reference.DeleteAsync();
            }
        }
    }
}