/*
 * ASCLITE
 * Author: Jerome Ajot, Jon Fiscus, Nicolas Radde, Chris Laprun
 *
 * This software was developed at the National Institute of Standards and Technology by 
 * employees of the Federal Government in the course of their official duties. Pursuant
 * to title 17 Section 105 of the United States Code this software is not subject to
 * copyright protection and is in the public domain. ASCLITE is an experimental system.
 * NIST assumes no responsibility whatsoever for its use by other parties, and makes no
 * guarantees, expressed or implied, about its quality, reliability, or any other
 * characteristic. We would appreciate acknowledgement if the software is used.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS."  With regard to this software, NIST MAKES NO EXPRESS
 * OR IMPLIED WARRANTY AS TO ANY MATTER WHATSOEVER, INCLUDING MERCHANTABILITY,
 * OR FITNESS FOR A PARTICULAR PURPOSE.
 */

#ifndef TEST_GRAPHALIGNEDTOKEN_H
#define TEST_GRAPHALIGNEDTOKEN_H

#include "stdinc.h"
#include "graphalignedtoken.h"
#include "speechset.h"

/**
 * Test the GraphAlignedSegment class
 */
class GraphAlignedTokenTest
{
	public:
		// class constructor
		GraphAlignedTokenTest();
		// class destructor
		~GraphAlignedTokenTest();
		/**
		 * Launch all the test methods on GraphAlignedToken
		 */
		void testAll();
		/**
		 * Test the behavior of the Equal operator on GraphAlignedToken
		 */
		void testEqualOperator();
};

#endif // TEST_GRAPHALIGNEDTOKEN_H
