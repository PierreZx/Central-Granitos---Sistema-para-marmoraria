using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Dashboard;

public partial class DashboardPage : ContentPage
{
	public DashboardPage(DashboardViewModel viewModel)
	{
		InitializeComponent();
		BindingContext = viewModel;
	}
}