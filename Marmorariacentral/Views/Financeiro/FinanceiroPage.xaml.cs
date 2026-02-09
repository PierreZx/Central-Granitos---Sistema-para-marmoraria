using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Financeiro;

public partial class FinanceiroPage : ContentPage
{
    public FinanceiroPage(FinanceiroViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}