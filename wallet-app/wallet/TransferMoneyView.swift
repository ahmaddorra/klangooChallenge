

import SwiftUI

struct TransferMoneyView: View {
    var headerView: some View{
        HStack{
            Text("Transfer Money")
                .font(.title)
                .fontWeight(.bold)
            Spacer()
        }
        
    }
    
    var body: some View {
        VStack{
            headerView
            ScrollView(.horizontal, showsIndicators: false){
                HStack(spacing: 15){
                    ForEach(1..<5){ num in
                        Image("user\(num)")
                            .resizable()
                            .frame(width: 50, height: 50)
                            .cornerRadius(10)
                    }
                    Button{}label: {
                        Image(systemName: "plus")
                            .imageScale(.small)
                            .foregroundColor(.black)
                    }.frame(width: 50, height: 50)
                        .background(Color.primaryYellow)
                        .cornerRadius(5)
                    
                }
            }
        }
    }
}

struct TransferMoneyView_Previews: PreviewProvider {
    static var previews: some View {
        TransferMoneyView()
    }
}
