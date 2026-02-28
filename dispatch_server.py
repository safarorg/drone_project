import csv
from drone import DeliveryException
from drone import Drone
from order import Order


class DispatchServer(object):

  def __init__(self, delivery_zones):
    self.delivery_zones = delivery_zones
    self.trips = []
    self.unpackaged_orders = []
    self.delivery_drone = Drone(delivery_zones)
    self.payload_test_drone = Drone(delivery_zones)

  def package_trips(self, most_optimal):
    """
    Uses build_trip (or build_most_optimal_trip) to organize the
    unpackaged orders into a list of packaged trips.
    """
    # Sort orders by submitted time
    self.unpackaged_orders.sort(key=lambda o: o.get_timestamp())

    while self.unpackaged_orders:
      trip = []

      # Build a trip
      if most_optimal:
        trip = self.build_most_optimal_trip()
      else:
        earliest_order = self.unpackaged_orders[0]
        trip = self.build_trip(earliest_order.get_delivery_zone())

      # Exit the loop if no orders are added to the trip
      if not trip:
        break

      for order in trip:
        self.unpackaged_orders.remove(order)

      self.trips.append(trip)

  def deliver_orders(self):
    """Uses the delivery_drone to deliver all of the packaged trips."""
    while self.trips:
      trip = self.trips[0]
      for order in trip:
        self.delivery_drone.add_order(order, 
          len(self.delivery_drone.get_orders()))
      try:
        self.trips.pop(0)
        self.delivery_drone.deliver_orders()  # Release the drone!
      except DeliveryException as e:
        print(e)
        return
      self.delivery_drone.recharge()

# 2.  In dispatch_server.py, implement the function:

#         build_trip(self, zone)

#     This function returns a list of orders to be delivered on the next drone trip.
#     The returned list of orders should contain as many of the oldest unpackaged
#     orders in the zone as possible without exceeding the drone's range. Once an
#     order exceeds the drone's range, any remaining capacity should be filled with
#     other orders destined for this same zone, from heaviest to lightest
#     (regardless of when the order was placed).

#     Make use of the payload_test_drone to simulate trips to determine whether the
#     delivery_drone will be able to accommodate an order. Remember to remove all
#     orders from the payload_test_drone after the trip is built!


  def build_trip(self, zone):
    """
    Returns a Trip containing as many of the oldest unpackaged Orders in the
    zone as possible without exceeding the drone's range. Once an order exceeds
    the drone's range, any remaining capacity should be filled with other orders
    destined for this same zone from heaviest to lightest (regardless of when
    the order was placed).
    """
    zone_orders = []
    for order in self.unpackaged_orders:
          if order.get_delivery_zone() == zone:
                zone_orders.append(order)
    
    ans = []
    for i in range(len(zone_orders)):
          zone_order = zone_orders[i]
          if self.payload_test_drone.simulate_trip_with_added_order(zone_order, i):
                ans.append(zone_order)
          else:
              break
    return ans

  def build_most_optimal_trip(self):
    """Returns the most optimal Trip."""
    # TODO: Implement
    return []

  def load_orders(self, csv_file_name):
    print('Loading order info from ' + csv_file_name)
    with open(csv_file_name, 'r') as csvfile:
      reader = csv.reader(csvfile, delimiter=',')
      for parsed_line in reader:
        self.add_order(int(parsed_line[0]),
                       int(parsed_line[1]),
                       int(parsed_line[2]),
                       int(parsed_line[3]),
                       int(parsed_line[4]),
                       parsed_line[5] == 'TRUE',
                       parsed_line[6] == 'TRUE', 
                       parsed_line[7] == 'TRUE',
                       parsed_line[8] == 'TRUE')

  def add_order(self, order_id=0, timestamp=0, zone=0,
                weight=0, user_id=0, subscriber=False, fragile=False,
                hazardous=False, perishable=False):

    order = Order(order_id, timestamp, zone, weight, user_id, subscriber,
                    fragile, hazardous, perishable)

    self.unpackaged_orders.append(order)
