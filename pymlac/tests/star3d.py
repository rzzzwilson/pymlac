#!/usr/bin/env python
"""
A cute 3D starfield effect.
My first experiment with PyGame, and the most Python I've ever written!
There's plenty of room for further optimization here, thats left as an exercise for the reader ;)
Will McGugan - will@willmcgugan.com
http://www.willmcgugan.com
"""

__copyright__ = "2005 Will McGugan"
__version__ = "1.0"
__license__ = "Public Domain"
__author__ = "Will McGugan"

import random, math, pygame
from pygame.locals import *


try:
    import psyco
    psyco.full()
except ImportError:
    print "This demo runs much smoother with the 'Psyco' module"
    print "You can get it from http://psyco.sourceforge.net/"

def DegreesToRadians( degrees ):
    "Converts an angle from degrees to radians."
    return degrees * ( math.pi / 180. )

# Look ma, globals!
# Some values you can fiddle with...

# Size of the window
# Actualy looks better in lo-res with chuncky pixels! (Try it in fullscreen)
SCREEN_WIDTH=       800	# 640
SCREEN_HEIGHT=      600	# 480
# 1 for fullscreen, 0 for windowed
FULLSCREEN_MODE=    1
# Stars per Z unit
STAR_DENSITY=       1
# Distance of far plane
STAR_DISTANCE=      4000.
# Field of view
FOV=                DegreesToRadians( 90. )
# Rotation speed of camera
ROTATION_SPEED=     DegreesToRadians( 40. )
# Speed of camera
SPEED=              2000.
# Use wu-pixels (anti-aliased points)
WU_PIXELS=          0

class Star( object ):
    "A 'star' here is just a point in 3D space."
    
    def __init__( self, x, y, z ):
        "Initialise a star at point x, y, z"
        self.x, self.y, self.z = x, y, z


    def render( self, surface, x, y, bright ):
        """Renders a star of brightness 'bright' at x, y.
        Uses 'wu-pixel' algorithm derived from http://freespace.virgin.net/hugo.elias/graphics/x_wupixl.htm
        Basically it draws a point at fractional coordinates."""      
        
        if not WU_PIXELS:
            b= int( min( 255., bright * 255. ) )
            surface.set_at( ( int(x), int(y) ), ( b, b, b ) )
            return
        
        if x >= 0. and x < SCREEN_WIDTH and y >= 0. and y < SCREEN_HEIGHT:
            # Get the fractional, and the whole part of the coordinates
            fx, ix = math.modf( x )
            fy, iy = math.modf( y )
            ix = int(ix)
            iy = int(iy)
            
            # Scale brightness (a value between 0 and 1), to a colour value (0-255)
            bright= min( bright*255., 255. )  
            
            # Calculate the brightness of each sub pixel, see the link above
            btl = int( (1.-fx) * (1.-fy) * bright )
            btr = int( fx * (1.-fy) * bright )
            bbl = int( (1.-fx)* fy * bright )
            bbr = int( fx * fy * bright )
            
            # Plot the pixel on screen
            surface.set_at( ( ix, iy ), ( btl, btl, btl ) )
            surface.set_at( ( ix+1, iy ), ( btr, btr, btr ) )
            surface.set_at( ( ix, iy+1 ), ( bbl, bbl, bbl ) )
            surface.set_at( ( ix+1, iy+1 ), ( bbr, bbr, bbr ) )     
        

class Starfield( object ):
    "Stores and renders starfield"
    
    def __init__( self, density = 1. ):
        "Density is in stars per unit of z"
        
        self.density = density

        # List of stars
        self.stars = []                
        
        # The point in the distance where we have generated new stars
        self.generated_z = 0


    def render( self, surface, fov, angle, position_z, distance ):
        "Renders all the stars."
    
        # Screen dimensions
        view_width = float( SCREEN_WIDTH )
        view_height = float( SCREEN_HEIGHT )
        
        # Aspect ratio of screen
        aspect = view_width / view_height
        
        # Calculate the distance where 3D units equal screen units
        view_distance = ( view_width / 2. ) / math.tan( fov / 2. )      
        
        # Calculate the maximum exents of projected pixels
        far_width = math.tan( fov / 2. ) * distance * 2.;
        far_height = far_width / aspect
        max_diameter = math.sqrt( far_width * far_width + far_height * far_height )
       
        # This is the radius of a cone that the camera would fit inside
        # Its used to cull stars that are no longer potentialy visible
        screen_radius= math.sqrt( view_width * view_width + view_height * view_height ) / 2.
        
        # Generate new stars in the distance, untill we have at least enough stars to render a screen-full
        generate_distance = 10
        while self.generated_z < position_z + distance:
            self.add_stars( self.generated_z, max_diameter, max_diameter, generate_distance )
            self.generated_z += generate_distance
        
        # clear screen
        background_colour = 0, 0, 0
        surface.fill( background_colour )
        
        # Adjustment required to put stars in the centre of the screen
        centre_x = view_width / 2.
        centre_y = view_height / 2.
        
        # Precalculate 1 over distance, because it is generally quicker to multiply by 1/x that it is to divide by x
        oodistance = 1. / distance
        
        # Create a list of all the stars which are currently visible, or could become visible
        visible_stars = []
        
        # Multiply brightness by constant scale so they are clearer
        bright_scale = 1.5
        
        # Precalculate sin and cos of the angle
        sin_angle= math.sin( angle )
        cos_angle= math.cos( angle )
        
        # Project ( transform 3D to 2D ) and render all stars       
        for star in self.stars:
            remove_star = False
            star_z= star.z - position_z
            # If the star is in front of the camera...
            if star.z > position_z + .1:
                # If it is within the visible z range...
                if star.z <= position_z + distance:
                    # Precalculate 1 over z
                    oostar_z = 1. / star_z
                    
                    screen_x = star.x * cos_angle - star.y * sin_angle
                    screen_y = star.x * sin_angle + star.y * cos_angle
                    
                    screen_x *= view_distance * oostar_z 
                    screen_y *= view_distance * oostar_z
                    
                    # If the star is within the camera cone...
                    if math.fabs( screen_x ) < screen_radius and math.fabs( screen_y ) < screen_radius:                    
                        star_z_over_distance= star_z * oodistance
                        # Calculate a brightness value so the stars fade in, rather than pop in
                        bright = ( 1. - star_z_over_distance * star_z_over_distance ) * bright_scale
                        star.render( surface, screen_x + centre_x, screen_y + centre_y, bright )
                    else:
                        # The star is out of the potentialy visible cone in front of the camera
                        remove_star = True
            else:
                # The star as behind the camera, and will not be seen again
                remove_star = True
            
            if not remove_star:
                visible_stars.append( star )
            
        # Replace star list with only visible stars, so we dont continue to process any stars no longer visible
        self.stars = visible_stars


    def add_stars( self, z, width, height, distance ):
        "Add random stars in to the distance."
        new_star_count = int( distance * self.density )
        centre_x = width / 2.
        centre_y = height / 2.        
        for _ in xrange( new_star_count ):
            new_star =   Star(  random.random() * width - centre_x,
                                random.random() * height - centre_y,
                                z + random.random() * distance )
            self.stars.append( new_star )        


def main():

    print "3D stars effect"
    print "Will McGugan will@willmcgugan.com"
    print "Try my game - Ping Ball (http://www.pingball.com )"
    print ""
    print "Move the mouse left and right to change rotation, up and down to change speed"
    print "Press (W) to toggle wu-pixels"

    random.seed()
    pygame.init()
    
    screen_dimensions= SCREEN_WIDTH, SCREEN_HEIGHT
    
    if FULLSCREEN_MODE:
        screen = pygame.display.set_mode( screen_dimensions, FULLSCREEN )
        pygame.mouse.set_visible( False )
    else:
        screen = pygame.display.set_mode( screen_dimensions )

    pygame.display.set_caption( '3D Stars Example' )

    backbuffer= pygame.Surface( screen_dimensions, SWSURFACE, screen )
    
    # Camera z
    # For this example x will be the width of the screen, y will be the height, and z will be 'in' the screen
    cam_z= 0.
    
    # Camera angle
    angle= 0.
    
    # Create a clock so we can position the camera correctly
    clock = pygame.time.Clock()    

    # Create our starfield
    starfield = Starfield( STAR_DENSITY )
    
    # So we can toggle wu-pixels
    global WU_PIXELS
    
    done= 0
    while not done:
        
        # Calculate the speed and rotation speed based on current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        half_width = float( SCREEN_WIDTH ) / 2.
        rotation_speed = ROTATION_SPEED * ( float( mouse_x ) - half_width ) / half_width ;
        camera_speed = SPEED * float( SCREEN_HEIGHT - mouse_y ) / float( SCREEN_HEIGHT )
        
        # Move the 'camera' forward, using the time and speed to calculate its position
        time_passed = clock.tick() / 1000.
        angle += time_passed * rotation_speed
        cam_z += time_passed * camera_speed        
        
        # Lock the display, render the stars        
        screen.lock()
        starfield.render( screen, FOV, angle, cam_z, STAR_DISTANCE )
        screen.unlock()
        
        # Flip next frame
        pygame.display.flip()
        
        # Process events
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = 1
                break
            elif e.type == KEYUP and e.key == K_w:
                WU_PIXELS = (1,0)[WU_PIXELS]
                print "Wu-pixels", ("off","on")[WU_PIXELS]


if __name__ == '__main__':
    main()

