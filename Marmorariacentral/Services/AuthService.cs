using System;
using System.Threading.Tasks;

namespace Marmorariacentral.Services
{
    public class AuthService
    {
        // Credenciais fixas conforme definido pelo Diretor
        private const string AdminEmail = "marmoraria.centralc@gmail.com";
        private const string AdminPassword = "MarmorariaC55";

        // Propriedade para verificar se existe um usuário logado na sessão atual
        public bool IsAuthenticated { get; private set; }

        /// <summary>
        /// Realiza o login validando as credenciais e salvando o estado
        /// </summary>
        public async Task<bool> LoginAsync(string email, string password)
        {
            // Simula um delay de rede para uma experiência de UI mais realista
            await Task.Delay(800);

            if (email.Trim().ToLower() == AdminEmail && password == AdminPassword)
            {
                IsAuthenticated = true;
                
                // Salva a preferência para o app lembrar que o usuário já logou (Persistência)
                Preferences.Default.Set("is_logged", true);
                Preferences.Default.Set("user_email", AdminEmail);
                
                return true;
            }

            IsAuthenticated = false;
            return false;
        }

        /// <summary>
        /// Limpa os dados da sessão
        /// </summary>
        public void Logout()
        {
            IsAuthenticated = false;
            Preferences.Default.Remove("is_logged");
            Preferences.Default.Remove("user_email");
        }

        /// <summary>
        /// Verifica se o usuário já estava logado anteriormente
        /// </summary>
        public bool CheckAutoLogin()
        {
            IsAuthenticated = Preferences.Default.Get("is_logged", false);
            return IsAuthenticated;
        }
    }
}