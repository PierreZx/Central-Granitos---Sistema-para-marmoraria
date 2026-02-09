using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Services;

namespace Marmorariacentral.ViewModels
{
    public partial class LoginViewModel : ObservableObject
    {
        private readonly AuthService _authService;

        [ObservableProperty]
        private string email = string.Empty;

        [ObservableProperty]
        private string senha = string.Empty;

        public LoginViewModel(AuthService authService)
        {
            _authService = authService;
        }

        // A lógica de login ficará aqui no futuro para um código 100% MVVM
    }
}