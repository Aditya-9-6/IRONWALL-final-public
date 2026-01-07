#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/in.h>
#include <linux/ip.h>


// Define a Hash Map to store blocked IPs
// Key: u32 (IP Address), Value: u32 (1 = Blocked)
BPF_HASH(blocked_ips, u32, u32);

int xdp_firewall(struct xdp_md *ctx) {
  // 1. Parse Ethernet Header
  void *data = (void *)(long)ctx->data;
  void *data_end = (void *)(long)ctx->data_end;

  struct ethhdr *eth = data;

  // Bounds Check: Ensure packet is large enough for Ethernet
  if (data + sizeof(*eth) > data_end)
    return XDP_PASS;

  // 2. Parse IP Header (Only handle IPv4 for now)
  if (eth->h_proto != htons(ETH_P_IP))
    return XDP_PASS;

  struct iphdr *ip = data + sizeof(*eth);

  // Bounds Check: Ensure packet is large enough for IP
  if (data + sizeof(*eth) + sizeof(*ip) > data_end)
    return XDP_PASS;

  // 3. Lookup Source IP in Block Map
  u32 src_ip = ip->saddr;
  u32 *lookup = blocked_ips.lookup(&src_ip);

  // 4. Decision
  if (lookup) {
    // IP Found in Block Map -> DROP PACKET
    return XDP_DROP;
  }

  // Default: Allow packet to pass to OS stack (and then to Python app)
  return XDP_PASS;
}
