using Microsoft.AspNetCore.SignalR;

namespace BlazorApp.Hubs
{
    public class ChatHub : Hub
    {
        public async Task SendMessage(string token,string user, string message)
        {
            await Clients.All.SendAsync("ReceiveMessage", user, message);
        }
    }
}