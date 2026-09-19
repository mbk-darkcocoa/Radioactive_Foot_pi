vm_os = ENV.fetch("VM_OS", "ubuntu").downcase
box_name = vm_os == "fedora" ? "fedora/40-cloud-base" : "ubuntu/jammy64"

Vagrant.configure("2") do |config|
  config.vm.box = box_name
  config.vm.hostname = "radioactive-foot-pi-#{vm_os}"

  if ENV.fetch("REAL_INTERNET", "0") == "1"
    bridge = ENV["BRIDGE_INTERFACE"]
    network_options = { type: "dhcp" }
    network_options[:bridge] = bridge if bridge && !bridge.empty?
    config.vm.network "public_network", **network_options
  end

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 4096
    vb.cpus = 2
  end

  config.vm.provision "shell", path: "deploy/vm/bootstrap.sh"
end
