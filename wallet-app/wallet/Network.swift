
import Foundation

class Network: ObservableObject{
    @Published var ad: Ad = Ad(url: "")
    var email = ""
    
    
    init(email: String) {
        self.email = email
        print(email)
    }
    
    func getAds() {
        print("-----------------------------------------------------------------------------------")
        guard let url = URL(string: "https://wallet-backend-dora.herokuapp.com/api/get-ad?email=\(self.email)") else { fatalError("Missing URL") }

            let urlRequest = URLRequest(url: url)

            let dataTask = URLSession.shared.dataTask(with: urlRequest) { (data, response, error) in
                if let error = error {
                    print("Request error: ", error)
                    return
                }

                guard let response = response as? HTTPURLResponse else { return }

//                if response.statusCode == 200 {
                    guard let data = data else { return }
                print(data)
                    DispatchQueue.main.async {
                        do {
                            let decodedAds = try JSONDecoder().decode(Ad.self, from: data)
                            self.ad = decodedAds
                            print("here")
                            print(self.ad.url)
                        } catch let error {
                            print("Error decoding: ", error)
                        }
                    }
//                }
            }

            dataTask.resume()
        }
    
}
