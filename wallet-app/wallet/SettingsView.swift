

import SwiftUI
import Combine

struct SettingsView: View {
    @EnvironmentObject var twitterAPI: TwitterAPI // 1
    
    
    var body: some View {
        NavigationView{
            Form{
                Section(header: Text("Display"), footer: Text("System settings will override Dark mode and use current device theme")){
                    Toggle(isOn: .constant(false), label: {
                        Text("Dark mode")
                    })
                    
                    Toggle(isOn: .constant(true), label: {
                        Text("Use system Settings")
                    })
                }
                
                Section{
                    Link("Link to Twitter", destination: URL(string: "https://wallet-backend-dora.herokuapp.com/authenticate/twitter")!)

                }.foregroundColor(.black)
                    .font(.system(size: 16, weight: .bold))
                
            }.navigationTitle("Settings ")
        }
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}
