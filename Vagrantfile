LAN_IP = ENV.fetch("RADIOACTIVE_FOOT_PI_LAN_IP", "192.168.56.10")
VM_CPUS = ENV.fetch("RADIOACTIVE_FOOT_PI_CPUS", "2").to_i
VM_MEMORY = ENV.fetch("RADIOACTIVE_FOOT_PI_MEMORY", "2048").to_i
VM_HOSTNAME = ENV.fetch("RADIOACTIVE_FOOT_PI_HOSTNAME", "radioactive-foot-pi")
VM_OS = ENV.fetch("RADIOACTIVE_FOOT_PI_OS", "ubuntu").downcase
WAN_BRIDGE = ENV["RADIOACTIVE_FOOT_PI_WAN_BRIDGE"]
WAN_ENABLED = %w[1 true yes on].include?(ENV.fetch("RADIOACTIVE_FOOT_PI_WAN", "false").downcase)

BOXES = {
  "ubuntu" => "bento/ubuntu-22.04",
  "fedora" => "bento/fedora-40"
}.freeze

box = BOXES.fetch(VM_OS) do
  raise "Unsupported RADIOACTIVE_FOOT_PI_OS '#{VM_OS}'. Supported values: #{BOXES.keys.join(', ')}"
end

Vagrant.configure("2") do |config|
  config.vm.box = box
  config.vm.hostname = VM_HOSTNAME

  config.vm.network "private_network", ip: LAN_IP

  if WAN_ENABLED
    public_network_options = {}
    public_network_options[:bridge] = WAN_BRIDGE if WAN_BRIDGE && !WAN_BRIDGE.empty?
    config.vm.network "public_network", **public_network_options
  end

  config.vm.provider "virtualbox" do |provider|
    provider.memory = VM_MEMORY
    provider.cpus = VM_CPUS
  end
end
